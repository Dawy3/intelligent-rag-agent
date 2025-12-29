"""
API endpoint tests
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns app info"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
@patch('app.api.v1.routes.get_agent_graph')
async def test_query_agent_success(mock_get_graph):
    """Test successful agent query"""
    # Mock agent graph response
    mock_graph = AsyncMock()
    mock_result = {
        "messages": [
            MagicMock(content="Test query"),
            MagicMock(content="Test answer", tool_calls=[])
        ]
    }
    mock_graph.ainvoke.return_value = mock_result
    mock_get_graph.return_value = mock_graph
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/agent/query",
            json={"query": "Test question", "session_id": "test123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "answer" in data
        assert "tool_used" in data
        assert "sources" in data
        assert "reasoning_steps" in data
        assert data["query"] == "Test question"
        assert data["answer"] == "Test answer"


@pytest.mark.asyncio
@patch('app.api.v1.routes.get_agent_graph')
async def test_query_agent_with_tools(mock_get_graph):
    """Test agent query that uses tools"""
    # Mock agent graph with tool calls
    mock_graph = AsyncMock()
    
    # Create mock message with tool calls
    mock_message_with_tools = MagicMock()
    mock_message_with_tools.tool_calls = [
        {"name": "search_knowledge_base"},
        {"name": "search_web"}
    ]
    mock_message_with_tools.content = "Based on the search results..."
    
    mock_result = {
        "messages": [
            MagicMock(content="Test query"),
            mock_message_with_tools,
            MagicMock(content="Final answer", tool_calls=[])
        ]
    }
    mock_graph.ainvoke.return_value = mock_result
    mock_get_graph.return_value = mock_graph
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/agent/query",
            json={"query": "What is in my documents?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "search_knowledge_base" in data["tool_used"]
        assert "search_web" in data["tool_used"]


@pytest.mark.asyncio
@patch('app.api.v1.routes.get_agent_graph')
async def test_query_agent_sql_tool(mock_get_graph):
    """Test agent query using SQL tool"""
    mock_graph = AsyncMock()
    
    mock_message_with_sql = MagicMock()
    mock_message_with_sql.tool_calls = [
        {"name": "sql_query_generator"}
    ]
    mock_message_with_sql.content = "Query results..."
    
    mock_result = {
        "messages": [
            MagicMock(content="Show me users"),
            mock_message_with_sql,
            MagicMock(content="Here are the users", tool_calls=[])
        ]
    }
    mock_graph.ainvoke.return_value = mock_result
    mock_get_graph.return_value = mock_graph
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/agent/query",
            json={"query": "Show me all users in the database"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "sql_query_generator" in data["tool_used"]


@pytest.mark.asyncio
async def test_query_agent_missing_query():
    """Test query endpoint with missing query field"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/agent/query",
            json={"session_id": "test123"}  # Missing query
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@patch('app.api.v1.routes.get_ingestion_service')
@patch('app.api.v1.routes.get_vector_store_service')
async def test_upload_document_success(mock_vector_service, mock_ingestion_service):
    """Test successful document upload"""
    # Mock services
    mock_ingestion = AsyncMock()
    mock_ingestion.process_pdf.return_value = {
        "doc_id": "test-doc-123",
        "chunks": [MagicMock()],
        "num_chunks": 5
    }
    mock_ingestion.cleanup_temp_file = MagicMock()
    mock_ingestion_service.return_value = mock_ingestion
    
    mock_vector = AsyncMock()
    mock_vector.add_documents = AsyncMock()
    mock_vector_service.return_value = mock_vector
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a fake PDF file
        files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        response = await client.post("/api/v1/documents/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "doc_id" in data
        assert "filename" in data
        assert "chunks_created" in data
        assert "status" in data
        assert data["status"] == "success"
        assert data["filename"] == "test.pdf"


@pytest.mark.asyncio
async def test_upload_document_missing_file():
    """Test upload endpoint without file"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/documents/upload")
        
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@patch('app.api.v1.routes.get_db_connection')
async def test_analytics_endpoint(mock_get_connection):
    """Test analytics endpoint"""
    # Mock database connection and queries
    mock_conn = AsyncMock()
    mock_conn.fetchval.side_effect = [100, 1.5]  # total_queries, avg_tools
    mock_conn.fetch.return_value = [
        {"tool_name": "search_knowledge_base", "usage_count": 60},
        {"tool_name": "search_web", "usage_count": 30},
        {"tool_name": "sql_query_generator", "usage_count": 10}
    ]
    mock_conn.close = AsyncMock()
    mock_get_connection.return_value = mock_conn
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/agent/analytics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_queries" in data
        assert "avg_tools_per_query" in data
        assert "tool_usage" in data
        assert data["total_queries"] == 100
        assert data["avg_tools_per_query"] == 1.5
        assert len(data["tool_usage"]) == 3


@pytest.mark.asyncio
@patch('app.api.v1.routes.get_db_connection')
async def test_analytics_database_error(mock_get_connection):
    """Test analytics endpoint handles database errors"""
    # Mock database error
    mock_conn = AsyncMock()
    mock_conn.fetchval.side_effect = Exception("Database connection failed")
    mock_conn.close = AsyncMock()
    mock_get_connection.return_value = mock_conn
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/agent/analytics")
        
        assert response.status_code == 500


@pytest.mark.asyncio
async def test_invalid_endpoint():
    """Test request to non-existent endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404


@pytest.mark.asyncio
@patch('app.api.v1.routes.get_agent_graph')
async def test_query_agent_error_handling(mock_get_graph):
    """Test agent query error handling"""
    # Mock agent to raise exception
    mock_graph = AsyncMock()
    mock_graph.ainvoke.side_effect = Exception("Agent processing error")
    mock_get_graph.return_value = mock_graph
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/agent/query",
            json={"query": "Test question"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_query_with_default_session():
    """Test query uses default session_id when not provided"""
    with patch('app.api.v1.routes.get_agent_graph') as mock_get_graph:
        mock_graph = AsyncMock()
        mock_result = {
            "messages": [
                MagicMock(content="Test"),
                MagicMock(content="Answer", tool_calls=[])
            ]
        }
        mock_graph.ainvoke.return_value = mock_result
        mock_get_graph.return_value = mock_graph
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/agent/query",
                json={"query": "Test"}  # No session_id
            )
            
            assert response.status_code == 200
            # Should use default session_id = "default"