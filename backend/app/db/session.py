"""
Database connection management
"""
import asyncpg
from app.config import get_settings


async def get_db_connection():
    """Create and return database connection"""
    setting = get_settings()
    return await asyncpg.connect(setting.database_url)

async def create_tables():
    """Create necessary database tables"""
    conn = await get_db_connection()
    
    try:
        # Create agent_queries table 
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_queries (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255),
                query TEXT NOT NULL,
                answer TEXT,
                tools_used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create agent_tool_usage table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_tool_usage (
                id SERIAL PRIMARY KEY,
                query_id INTEGER REFERENCES agent_queries(id),
                tool_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )              
       """)
        
        print("Database tables created successfully")
    finally:
        await conn.close()