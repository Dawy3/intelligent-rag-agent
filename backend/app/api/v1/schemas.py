"""
API request/response shemas
"""
from pydantic import BaseModel

class QueryRequest(BaseModel):
    """Request model for agent queries"""
    query: str
    session_id : str = "default"
    

class QueryResponse(BaseModel):
    """Response model for agent queries"""
    query: str
    answer : str
    tool_used : list[str]
    sources: list[str]
    reasoning_steps: int
    
class DocumentUploadResponse(BaseModel):
    """Response model for document uploads"""
    doc_id : str
    filename : str
    chunks_created: int
    status: str
    
    
class ToolUsage(BaseModel):
    """Tool usage statistics"""
    tool:str
    count : int
    
class AnalyticsResponse(BaseModel):
    """Response model for analytics"""
    total_queries: int
    avg_tools_per_query: float
    tool_usage: list[ToolUsage]