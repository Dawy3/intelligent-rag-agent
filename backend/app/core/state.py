"""
Agent State Defination 
"""
from typing import Annotated, Sequence, TypedDict, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    tool_calls_made: int
    source_used : List[str]