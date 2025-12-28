"""
Database models (SQLAlchemy or documentation)

Note: Using asyncpg directly for simplicity.
For more complex applications, consider using SQLAlchemy with asyncpg.

Table Schemas:
--------------

agent_queries:
    - id: SERIAL PRIMARY KEY
    - session_id: VARCHAR(255)
    - query: TEXT NOT NULL
    - answer: TEXT
    - tools_used: INTEGER DEFAULT 0
    - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

agent_tool_usage:
    - id: SERIAL PRIMARY KEY
    - query_id: INTEGER REFERENCES agent_queries(id)
    - tool_name: VARCHAR(100) NOT NULL
    - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""

# If using SQLAlchemy, define models here
# Example:
# from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime

# Base = declarative_base()

# class AgentQuery(Base):
#     __tablename__ = "agent_queries"
    
#     id = Column(Integer, primary_key=True, index=True)
#     session_id = Column(String(255))
#     query = Column(Text, nullable=False)
#     answer = Column(Text)
#     tools_used = Column(Integer, default=0)
#     created_at = Column(DateTime, default=datetime.utcnow)