"""
Agent tools and node definitions
"""
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode
from app.services.vector_store import get_vector_store_service
from app.config import get_settings
from app.services.sql_service import get_sql_service
from app.services.llm import get_llm

@tool
async def search_knowledge_base(query: str) -> str:
    """Search the internal knowledge base for relevant documents.
    Use this when the user asks about documents you have or internal information."""
    setting = get_settings()
    vector_service = get_vector_store_service()
    docs = await vector_service.similarity_search(query, k=setting.similarity_search_k)
    
    if not docs:
        return "No relevant documents found in knowledge base."
    
    results = "\n\n".join([
        f"Document {i+1} (from {doc.metadata.get('filename','unknown')}):\n{doc.page_content}"
        for i, doc in enumerate(docs)
    ])
    
    return f"Knowledge Base Results: \n{results}"

@tool
async def search_web(query:str) -> str:
    """Search the web for current information, news, or facts not in the knowledge base.
    Use this for recent events, real-time data, or when knowledge base has no results."""
    
    settings=  get_settings()
    searrch_tool = TavilySearchResults(
        max_results=settings.web_search_max_results,
        search_depth= "advanced",
        include_answer= True,
        include_raw_content=True
    )    
    
    results = await searrch_tool.ainvoke({"query": query})
    
    formatted = []
    for r in results:
        formatted.append(
            f"Source: {r.get('url', 'N/A')}\n"
            f"Title: {r.get('title', 'N/A')}\n"
            f"Content: {r.get('content', 'N/A')}\n"
        )
        
    return "Web Search Results:\n" + "\n---\n".join(formatted)


@tool
async def sql_query_generator(natural_language_query: str) -> str:
    """Generate and execute SQL queries from natural language.
    Use this when the user asks questions about database data, wants to query tables,
    or needs data analysis from the database.
    
    Examples:
    - "Show me all users who signed up last month"
    - "What are the top 5 products by sales?"
    - "Count how many orders were placed yesterday"
    """
    
    try:
        sql_service = get_sql_service()
        llm = get_llm()
        
        # Get database schema
        schema = await sql_service.get_schema_info()
        
        # Generate SQL query using LLM
        prompt = f"""Given this database schema:

{schema}

Generate a SQL query for this request: "{natural_language_query}"

Requirements:
- Return ONLY the SQL query, no explanation
- Use standard PostgreSQL syntax
- Only SELECT queries (no INSERT, UPDATE, DELETE)
- Be precise and efficient

SQL Query:"""
        
        response = await llm.ainvoke(prompt)
        sql_query = response.content.strip()
        
        # Clean up the query (remove markdown if present)
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        # Execute the query
        result = await sql_service.execute_query(sql_query)
        
        if "error" in result:
            return f"Error executing query: {result['error']}\nGenerated Query: {result['query']}"
        
        # Format results
        formatted_results = f"Query executed successfully!\n\n"
        formatted_results += f"SQL Query: {result['query']}\n"
        formatted_results += f"Rows returned: {result['row_count']}\n\n"
        
        if result['results']:
            formatted_results += "Results:\n"
            for i, row in enumerate(result['results'][:10], 1):  # Show first 10
                formatted_results += f"{i}. {row}\n"
            
            if result['row_count'] > 10:
                formatted_results += f"\n... and {result['row_count'] - 10} more rows"
        else:
            formatted_results += "No results found."
        
        return formatted_results
        
    except Exception as e:
        return f"Error in SQL query generation: {str(e)}"
    
    
def get_tools():
    """Get list of availabe tools"""
    return [search_knowledge_base, search_web, sql_query_generator]

def get_tool_node():
    """Get tool node for graph"""
    return ToolNode(get_tools())