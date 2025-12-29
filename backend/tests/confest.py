"""
Pytest configuration and shared fixtures
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock application settings"""
    settings = MagicMock()
    settings.app_title = "Test App"
    settings.app_version = "1.0.0"
    settings.openrouter_api_key = "test-key"
    settings.openrouter_base_url = "https://test.com"
    settings.model_name = "test-model"
    settings.llm_temperature = 0.0
    settings.pinecone_api_key = "test-pinecone-key"
    settings.pinecone_index_name = "test-index"
    settings.pinecone_cloud = "aws"
    settings.pinecone_region = "us-east-1"
    settings.pinecone_metric = "cosine"
    settings.embedding_model_name = "test-embedding-model"
    settings.embedding_device = "cpu"
    settings.chunk_size = 1000
    settings.chunk_overlap = 200
    settings.similarity_search_k = 4
    settings.web_search_max_results = 3
    settings.database_url = "postgresql://test:test@localhost/test"
    settings.sql_tool_database_url = "postgresql://test:test@localhost/test_data"
    settings.sql_tool_enabled = True
    settings.sql_tool_read_only = True
    return settings


@pytest.fixture
def mock_vector_store():
    """Mock vector store service"""
    mock_store = AsyncMock()
    mock_store.similarity_search = AsyncMock(return_value=[])
    mock_store.add_documents = AsyncMock(return_value=["doc_id_1"])
    return mock_store


@pytest.fixture
def mock_llm():
    """Mock LLM"""
    mock = AsyncMock()
    mock.ainvoke = AsyncMock()
    return mock


@pytest.fixture
def mock_database_connection():
    """Mock database connection"""
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock()
    mock_conn.fetch = AsyncMock()
    mock_conn.execute = AsyncMock()
    mock_conn.close = AsyncMock()
    return mock_conn


@pytest.fixture
def sample_document():
    """Sample document for testing"""
    doc = MagicMock()
    doc.page_content = "This is a test document about artificial intelligence."
    doc.metadata = {
        "filename": "test.pdf",
        "doc_id": "test-doc-123",
        "page": 1
    }
    return doc


@pytest.fixture
def sample_documents():
    """Multiple sample documents"""
    docs = []
    for i in range(3):
        doc = MagicMock()
        doc.page_content = f"Document {i+1} content about AI and machine learning."
        doc.metadata = {
            "filename": f"test{i+1}.pdf",
            "doc_id": f"doc-{i+1}",
            "page": 1
        }
        docs.append(doc)
    return docs


@pytest.fixture
def sample_web_search_results():
    """Sample web search results"""
    return [
        {
            "url": "https://example.com/article1",
            "title": "AI Developments",
            "content": "Recent advances in artificial intelligence..."
        },
        {
            "url": "https://example.com/article2",
            "title": "Machine Learning News",
            "content": "New breakthroughs in ML research..."
        }
    ]


@pytest.fixture
def sample_sql_results():
    """Sample SQL query results"""
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
    ]


@pytest.fixture
def mock_agent_state():
    """Mock agent state"""
    from langchain_core.messages import HumanMessage
    
    return {
        "messages": [HumanMessage(content="Test question")],
        "tool_calls_made": 0,
        "sources_used": []
    }


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances before each test"""
    # Reset vector store singleton
    import app.services.vector_store as vs_module
    vs_module._vector_store_service = None
    
    # Reset SQL service singleton
    import app.services.sql_service as sql_module
    sql_module._sql_service = None
    
    # Reset agent graph singleton
    import app.core.graph as graph_module
    graph_module._agent_graph = None
    
    yield
    
    # Cleanup after test if needed


@pytest.fixture
def temp_pdf_file(tmp_path):
    """Create a temporary PDF file for testing"""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\nFake PDF content for testing")
    return str(pdf_path)


# Marker for integration tests
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring external services"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Skip integration tests by default
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers"""
    skip_integration = pytest.mark.skip(reason="Integration tests require --run-integration flag")
    
    for item in items:
        if "integration" in item.keywords and not config.getoption("--run-integration", default=False):
            item.add_marker(skip_integration)


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require external services"
    )