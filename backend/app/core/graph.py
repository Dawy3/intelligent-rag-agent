"""
LangGraph graph construction and agent workflow
"""
from typing import Literal
from langgraph.graph import StateGraph, START, END
from app.core.state import AgentState
from app.core.agents import get_tools, get_tool_node
from app.services.llm import get_llm_with_tools


def create_intelligent_agent():
    """Create an agent that intelligently decide which tools to use"""

    tools = get_tools()
    tool_node = get_tool_node()
    llm_with_tools = get_llm_with_tools(tools)
    
    # Agent Node - decide what to do
    async def agent(state:AgentState):
        """Agent reasoning node"""
        messages = state['messages']
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}
    
    # Router - decide whether to use tools of finish
    def should_continue(state: AgentState) -> Literal["tools" , "end"]:
        """Determine if agent should continue to tools or end"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # if there are tools calls cotinue tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        
        # Otherwise, end
        return "end"
    
    # Build Graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("tools", tool_node)
    graph.add_node("agent", agent)
    
    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools" : "tools",
            "end": END
        }
    )
    graph.add_edge("tools", "agent") # After tools, go back to agent 
    
    return graph.compile()


# Global instance
_agent_graph= None

def get_agent_graph():
    """Get or create agent graph instance"""
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = create_intelligent_agent()
        
    return _agent_graph
     
    