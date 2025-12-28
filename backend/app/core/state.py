"""
Agent State Defination 
"""
from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    tool_calls_made: int
    source_used : List[str]