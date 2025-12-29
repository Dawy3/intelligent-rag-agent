"""
Agent and tool tests
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from app.core.agents import (
    search_knowledge_base,
    search_web,
    sql_query_generator,
    get_tools,
    get_tool_node
)
from app.core.graph import create_intelligent_agent, get_agent_graph
from app.core.state import AgentState


# ========== Tool Tests ==========

@pytest.mark.asyncio
@patch('app.core.agents.get_vector_store_service')
async def test_search_knowledge_base_with_results(mock_vector_service):
    """Test knowledge base search returns documents"""
    # Mock vector store service
    mock_service = AsyncMock()
    mock_doc1 = MagicMock()
    mock_doc1.page_content = "This is a test document about AI"
    mock_doc1.metadata = {"filename": "test.pdf"}
    
    mock_doc2 = MagicMock()
    mock_doc2.page_content = "Another document about machine learning"
    mock_doc2.metadata = {"filename": "ml.pdf"}
    
    mock_service.similarity_search.return_value = [mock_doc1, mock_doc2]
    mock_vector_service.return_value = mock_service
    
    # Test the tool
    result = await search_knowledge_base.ainvoke({"query": "What is AI?"})
    
    assert "Knowledge Base Results:" in result
    assert "test.pdf" in result
    assert "ml.pdf" in result
    assert "This is a test document about AI" in result
    assert "Another document about machine learning" in result


@pytest.mark.asyncio
@patch('app.core.agents.get_vector_store_service')
async def test_search_knowledge_base_no_results(mock_vector_service):
    """Test knowledge base search with no documents found"""
    mock_service = AsyncMock()
    mock_service.similarity_search.return_value = []
    mock_vector_service.return_value = mock_service
    
    result = await search_knowledge_base.ainvoke({"query": "Nonexistent topic"})
    
    assert "No relevant documents found" in result


@pytest.mark.asyncio
@patch('app.core.agents.TavilySearchResults')
async def test_search_web_success(mock_tavily):
    """Test web search returns results"""
    # Mock Tavily search results
    mock_search_tool = AsyncMock()
    mock_search_tool.ainvoke.return_value = [
        {
            "url": "https://example.com/article1",
            "title": "AI News",
            "content": "Latest developments in AI..."
        },
        {
            "url": "https://example.com/article2",
            "title": "Tech Update",
            "content": "New technology trends..."
        }
    ]
    mock_tavily.return_value = mock_search_tool
    
    result = await search_web.ainvoke({"query": "latest AI news"})
    
    assert "Web Search Results:" in result
    assert "https://example.com/article1" in result
    assert "AI News" in result
    assert "Latest developments in AI" in result


@pytest.mark.asyncio
@patch('app.core.agents.get_sql_service')
@patch('app.core.agents.get_llm')
async def test_sql_query_generator_success(mock_get_llm, mock_get_sql_service):
    """Test SQL query generator with successful execution"""
    # Mock SQL service
    mock_sql_service = AsyncMock()
    mock_sql_service.get_schema_info.return_value = "Table: users\nColumns: id (int), name (text)"
    mock_sql_service.execute_query.return_value = {
        "success": True,
        "query": "SELECT * FROM users LIMIT 10",
        "row_count": 10,
        "results": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
    }
    mock_get_sql_service.return_value = mock_sql_service
    
    # Mock LLM
    mock_llm = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = "SELECT * FROM users LIMIT 10"
    mock_llm.ainvoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm
    
    result = await sql_query_generator.ainvoke({
        "natural_language_query": "Show me all users"
    })
    
    assert "Query executed successfully" in result
    assert "SELECT * FROM users LIMIT 10" in result
    assert "Rows returned: 10" in result
    assert "Alice" in result
    assert "Bob" in result


@pytest.mark.asyncio
@patch('app.core.agents.get_sql_service')
@patch('app.core.agents.get_llm')
async def test_sql_query_generator_with_error(mock_get_llm, mock_get_sql_service):
    """Test SQL query generator handles execution errors"""
    mock_sql_service = AsyncMock()
    mock_sql_service.get_schema_info.return_value = "Table: users"
    mock_sql_service.execute_query.return_value = {
        "error": "Syntax error in SQL query",
        "query": "INVALID SQL"
    }
    mock_get_sql_service.return_value = mock_sql_service
    
    mock_llm = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = "INVALID SQL"
    mock_llm.ainvoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm
    
    result = await sql_query_generator.ainvoke({
        "natural_language_query": "Bad query"
    })
    
    assert "Error executing query" in result
    assert "Syntax error" in result


@pytest.mark.asyncio
@patch('app.core.agents.get_sql_service')
@patch('app.core.agents.get_llm')
async def test_sql_query_generator_no_results(mock_get_llm, mock_get_sql_service):
    """Test SQL query with no results"""
    mock_sql_service = AsyncMock()
    mock_sql_service.get_schema_info.return_value = "Table: users"
    mock_sql_service.execute_query.return_value = {
        "success": True,
        "query": "SELECT * FROM users WHERE id = 999",
        "row_count": 0,
        "results": []
    }
    mock_get_sql_service.return_value = mock_sql_service
    
    mock_llm = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = "SELECT * FROM users WHERE id = 999"
    mock_llm.ainvoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm
    
    result = await sql_query_generator.ainvoke({
        "natural_language_query": "Find user 999"
    })
    
    assert "No results found" in result


def test_get_tools():
    """Test get_tools returns all expected tools"""
    tools = get_tools()
    
    assert len(tools) == 3
    tool_names = [tool.name for tool in tools]
    assert "search_knowledge_base" in tool_names
    assert "search_web" in tool_names
    assert "sql_query_generator" in tool_names


def test_get_tool_node():
    """Test tool node creation"""
    tool_node = get_tool_node()
    assert tool_node is not None


# ========== Graph Tests ==========

@patch('app.core.graph.get_llm_with_tools')
@patch('app.core.graph.get_tool_node')
def test_create_intelligent_agent(mock_tool_node, mock_llm_with_tools):
    """Test agent graph creation"""
    mock_llm_with_tools.return_value = AsyncMock()
    mock_tool_node.return_value = MagicMock()
    
    graph = create_intelligent_agent()
    
    assert graph is not None


@patch('app.core.graph.get_llm_with_tools')
@patch('app.core.graph.get_tool_node')
def test_get_agent_graph_singleton(mock_tool_node, mock_llm_with_tools):
    """Test agent graph is singleton"""
    mock_llm_with_tools.return_value = AsyncMock()
    mock_tool_node.return_value = MagicMock()
    
    # Clear any existing instance
    import app.core.graph as graph_module
    graph_module._agent_graph = None
    
    graph1 = get_agent_graph()
    graph2 = get_agent_graph()
    
    assert graph1 is graph2


@pytest.mark.asyncio
@patch('app.core.graph.get_llm_with_tools')
@patch('app.core.graph.get_tool_node')
async def test_agent_without_tool_calls(mock_tool_node, mock_llm_with_tools):
    """Test agent finishes without tool calls"""
    # Mock LLM that returns answer without tool calls
    mock_llm = AsyncMock()
    mock_response = AIMessage(content="Direct answer")
    mock_llm.ainvoke.return_value = mock_response
    mock_llm_with_tools.return_value = mock_llm
    
    mock_tool_node.return_value = MagicMock()
    
    graph = create_intelligent_agent()
    
    initial_state: AgentState = {
        "messages": [HumanMessage(content="Simple question")],
        "tool_calls_made": 0,
        "sources_used": []
    }
    
    result = await graph.ainvoke(initial_state)
    
    assert "messages" in result
    assert len(result["messages"]) >= 2  # At least input and output


@pytest.mark.asyncio
@patch('app.core.graph.get_llm_with_tools')
@patch('app.core.agents.get_vector_store_service')
async def test_agent_with_knowledge_base_tool(mock_vector_service, mock_llm_with_tools):
    """Test agent uses knowledge base tool"""
    # Mock vector store
    mock_service = AsyncMock()
    mock_doc = MagicMock()
    mock_doc.page_content = "Test content"
    mock_doc.metadata = {"filename": "test.pdf"}
    mock_service.similarity_search.return_value = [mock_doc]
    mock_vector_service.return_value = mock_service
    
    # Mock LLM with tool call then final answer
    mock_llm = AsyncMock()
    
    # First call: agent decides to use tool
    mock_tool_call_response = AIMessage(content="")
    mock_tool_call_response.tool_calls = [
        {"name": "search_knowledge_base", "args": {"query": "test"}, "id": "call_1"}
    ]
    
    # Second call: agent provides final answer
    mock_final_response = AIMessage(content="Based on the document: test content")
    
    mock_llm.ainvoke.side_effect = [mock_tool_call_response, mock_final_response]
    mock_llm_with_tools.return_value = mock_llm
    
    graph = create_intelligent_agent()
    
    initial_state: AgentState = {
        "messages": [HumanMessage(content="What's in my documents?")],
        "tool_calls_made": 0,
        "sources_used": []
    }
    
    result = await graph.ainvoke(initial_state)
    
    assert "messages" in result
    # Should have multiple messages: input, tool call, tool result, final answer
    assert len(result["messages"]) >= 3


def test_agent_state_structure():
    """Test AgentState has correct structure"""
    state: AgentState = {
        "messages": [HumanMessage(content="test")],
        "tool_calls_made": 0,
        "sources_used": []
    }
    
    assert "messages" in state
    assert "tool_calls_made" in state
    assert "sources_used" in state
    assert isinstance(state["messages"], list)
    assert isinstance(state["tool_calls_made"], int)
    assert isinstance(state["sources_used"], list)


@pytest.mark.asyncio
async def test_tool_descriptions():
    """Test all tools have proper descriptions"""
    tools = get_tools()
    
    for tool in tools:
        assert tool.name is not None
        assert tool.description is not None
        assert len(tool.description) > 20  # Meaningful description
        
        # Check specific tool descriptions
        if tool.name == "search_knowledge_base":
            assert "internal knowledge base" in tool.description.lower()
        elif tool.name == "search_web":
            assert "web" in tool.description.lower()
        elif tool.name == "sql_query_generator":
            assert "sql" in tool.description.lower() or "database" in tool.description.lower()