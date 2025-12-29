"""
API routes and endpoints
"""
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_core.messages import HumanMessage

from app.api.v1.schemas import (
    QueryRequest,
    QueryResponse,
    DocumentUploadResponse,
    AnalyticsResponse,
    ToolUsage   
)
from app.core.graph import get_agent_graph
from app.core.prompts import get_system_message
from app.services.vector_store import get_vector_store_service
from app.services.ingestion import get_ingestion_service
from app.db.session import get_db_connection

router = APIRouter()

@router.post("/agent/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """Query the intelligent RAG agent"""
    
    try:
        agent_graph = get_agent_graph()
        
        # Prepare initial state
        initial_state = {
            "messages" : [
                get_system_message(),
                HumanMessage(request.query)
            ],
            "tool_calls_made": 0,
            "sources_used" : []
        }
        
        # Run the Agent
        result = await agent_graph.ainvoke(initial_state)
        
        # Extract answer and metadata
        messages = result['messages']
        final_answer = messages[-1].content
        
        # Track which tools were used
        tool_used = []
        sources = []
        
        for msg in messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.get("name", "unknown")
                    if tool_name not in tool_used:
                        tool_used.append(tool_name)
                        
        return QueryResponse(
            query = request.query,
            answer= final_answer,
            tool_used= tool_used,
            sources= sources,
            reasoning_steps= len(messages) // 2
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail= str(e))
    
    
@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process document"""
    
    ingestion_service = get_ingestion_service()
    vector_service = get_vector_store_service()
    
    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix =f"_{file.filename}") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
        
    try:
        # Process document
        result = await ingestion_service.process_pdf(tmp_path, file.filename)
        
        # Store in vector database
        await vector_service.add_documents(result["chunks"])
        
        # Cleanup
        ingestion_service.cleanup_temp_file(tmp_path)
        
        return DocumentUploadResponse(
            doc_id = result["doc_id"],
            filename= file.filename,
            chunks_created= result["num_chunks"],
            status= "success"
        )
        
    except Exception as e:
        ingestion_service.cleanup_temp_file(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/agent/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """Get agent usage analytics"""
    
    conn = await get_db_connection()
    
    try:
        # Total queries
        total_queries = await conn.fetchval(
            "SELECT COUNT(*) FROM agent_queries"
        )
        
        # Average tools per query
        avg_tools_per_query = await conn.fetchval(
            "SELECT AVG(tool_used) FROM agent_queries"
        )
        
        # Tool usage breakdown
        tool_usage_rows  = await conn.fetch( # List of rows
            """SELECT tool_name, COUNT(*) as usage_count
                FROM agent_tool_usage
                GROUP BY tool_name
                ORDER BY usage_count DESC"""
        )
        
        tool_usage = [
            ToolUsage(tool=row['tool_name'], count= row['usage_count'])
            for row in tool_usage_rows
        ]
        
        return AnalyticsResponse(
            total_queries=total_queries or 0,
            avg_tools_per_query=round(avg_tools_per_query or 0, 2),
            tool_usage=tool_usage
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()
    
