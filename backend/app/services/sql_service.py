"""
SQL query generation and execution service
"""
import asyncpg
from typing import Optional, List, Dict, Any
from app.config import get_settings

class SQLService:
    """Service for SQL query generation and execution"""
    
    def __init__(self):
        self.setting =get_settings()
        self._connection_pool = None
        
    async def get_connection(self):
        """Get database connection"""
        if not self.setting.sql_tool_database_url:
            raise ValueError("SQL_TOOL_DATABASE_URL not configured")
        return await asyncpg.connect(self.setting.sql_tool_database_url)
    
    async def get_shema_info(self) -> str:
        """Get database schema information for context"""
        conn = await self.get_connection()
        try:
            # Get all tables
            tables = await conn.fetch("""
                    SELECT table_name
                    FROM infromation_schema.table
                    WHERE table_schema = 'public'
                                      """)

            schema_info = []
            for table in tables:
                table_name = table['table_name']
                
                # Get column for each table
                columns = await conn.fetch("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_name = 1$
                                           """, table_name)
                
                cols = [f"{c['column_name']} ({c['data_type']})" for c in columns]
                schema_info.append(f"Table: {table_name}\nColumns: {', '.join(cols)}")
                
            return "\n\n".join(schema_info)
        finally:
            await conn.close()
        
        
        
async def execute_query(self, sql_query: str) -> Dict[str, Any]:
    """Execute SQL query safely"""
    # Safety check: only allow SELECT queries
    if self.settings.sql_tool_read_only:
        if not sql_query.strip().upper().startswith('SELECT'):
            return {
                "error": "Only SELECT queries are allowed for safety",
                "query": sql_query
            }
    
    conn = await self.get_connection()
    try:
        # Execute query
        rows = await conn.fetch(sql_query)
        
        # Convert to list of dicts
        results = [dict(row) for row in rows]
        
        return {
            "success": True,
            "query": sql_query,
            "row_count": len(results),
            "results": results[:100]  # Limit to 100 rows for safety
        }
    except Exception as e:
        return {
            "error": str(e),
            "query": sql_query
        }
    finally:
        await conn.close()


_sql_service = None

def get_sql_service() -> SQLService:
    """Get SQL service instance"""
    global _sql_service
    if _sql_service is None:
        _sql_service = SQLService()
    return _sql_service