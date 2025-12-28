"""
Application Configuration and setting 
"""
import os 
from functools import lru_cache # Least Recently Used cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application setting load from enviornment variables"""
    
    # API Configuration
    app_title: str = "Intelligent RAG Agent"
    app_version: str = "1.0.0"
    
    # OpenRouter/LLM Configuration
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    model_name:str = os.getenv("MODEL_NAME")
    llm_temperature: float = 0.0
    
    # Pinecone Configuration
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_index_name: str = "intelligent-rag"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    pinecone_metric: str = "cosine"
    
    # Embedding Configuration
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device : str = "cpu"
    
    # Document Processing 
    chunk_size : int =  1000
    chunk_overlap : int = 200
    
    # Search Configuration
    similarity_search_k: int = 4
    web_search_max_results: int = 3
    
    # Database Configuration
    database_url : str = os.getenv("DATABASE_URL", "")
    
    # Tavily Search
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    
    # SQL Query Tool Configuration (separate from analytics DB)
    sql_tool_database_url: str = os.getenv("SQL_TOOL_DATABASE_URL", "")
    sql_tool_enabled: bool = os.getenv("SQL_TOOL_ENABLED", "true").lower() == "true"
    sql_tool_allowed_tables: list = []  # Empty = all tables allowed
    sql_tool_read_only: bool = True  # Safety: only SELECT queries
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        

@lru_cache
def get_settings() -> Settings:
    """Get cashed setting instance"""
    return Settings()
    
    