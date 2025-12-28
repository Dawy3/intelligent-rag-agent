# Intelligent RAG Agent

An intelligent Retrieval-Augmented Generation (RAG) agent powered by LangGraph that intelligently decides which tools to use for answering queries.

## Features

- 🤖 **Intelligent Agent**: Uses LangGraph to orchestrate tool usage
- 📚 **Knowledge Base**: Vector store with Pinecone for document search
- 🌐 **Web Search**: Real-time information via Tavily
- 🗄️ **SQL Query Generator**: Natural language to SQL queries with execution
- 📄 **Document Processing**: PDF upload and chunking
- 📊 **Analytics**: Track agent usage and tool statistics

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration management
│   ├── api/v1/              # API layer
│   │   ├── routes.py        # Endpoints
│   │   └── schemas.py       # Pydantic models
│   ├── core/                # AI logic
│   │   ├── agents.py        # Tool definitions
│   │   ├── graph.py         # LangGraph workflow
│   │   ├── prompts.py       # System prompts
│   │   └── state.py         # Agent state
│   ├── services/            # External integrations
│   │   ├── llm.py           # LLM service
│   │   ├── vector_store.py  # Vector database
│   │   └── ingestion.py     # Document processing
│   ├── db/                  # Database layer
│   │   ├── models.py        # Data models
│   │   └── session.py       # DB connections
│   └── utils/               # Utilities
│       └── logging.py       # Logging setup
└── requirements.txt
```

## Prerequisites

- Python 3.11+
- PostgreSQL
- API Keys:
  - OpenRouter or OpenAI
  - Pinecone
  - Tavily

## Setup

### 1. Clone and Navigate

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env` template and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENROUTER_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/intelligent_rag
SQL_TOOL_DATABASE_URL=postgresql://user:password@localhost:5432/your_data_db
MODEL_NAME=openai/gpt-4
```

### 5. Setup Database

Create PostgreSQL database:

```sql
CREATE DATABASE intelligent_rag;
```

Tables will be created automatically on first run.

## Running the Application

### Development Mode

```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## API Endpoints

### Query Agent

```bash
POST /api/v1/agent/query
```

**Request:**
```json
{
  "query": "What are the latest developments in AI?",
  "session_id": "user123"
}
```

**Response:**
```json
{
  "query": "What are the latest developments in AI?",
  "answer": "Based on recent information...",
  "tool_used": ["search_web"],
  "sources": [],
  "reasoning_steps": 2
}
```

### Upload Document

```bash
POST /api/v1/documents/upload
```

**Request:**
- Form data with PDF file

**Response:**
```json
{
  "doc_id": "uuid-here",
  "filename": "document.pdf",
  "chunks_created": 42,
  "status": "success"
}
```

### Get Analytics

```bash
GET /api/v1/agent/analytics
```

**Response:**
```json
{
  "total_queries": 150,
  "avg_tools_per_query": 1.5,
  "tool_usage": [
    {"tool": "search_knowledge_base", "count": 120},
    {"tool": "search_web", "count": 85},
    {"tool": "sql_query_generator", "count": 45}
  ]
}
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

Example test:

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_query_agent():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/agent/query",
            json={"query": "How many users are in the database?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "sql_query_generator" in data["tool_used"]
```

## Configuration

All configuration is managed in `app/config.py`:

- **LLM Settings**: Model, temperature, API keys
- **Vector Store**: Pinecone configuration
- **Document Processing**: Chunk size, overlap
- **Search**: Results limits
- **SQL Tool**: Database connection, safety settings

Override via environment variables.

## Development

### Adding New Tools

1. Define tool in `app/core/agents.py`:

```python
@tool
async def my_new_tool(input: str) -> str:
    """Tool description for the agent"""
    # Implementation
    return result
```

2. Add to tools list in `get_tools()`

### Adding New Endpoints

1. Define schemas in `app/api/v1/schemas.py`
2. Add route in `app/api/v1/routes.py`

### Modifying Agent Behavior

- Edit system prompt in `app/core/prompts.py`
- Modify graph logic in `app/core/graph.py`

## Troubleshooting

### Vector Store Issues

```bash
# Check Pinecone index
python -c "from app.services.vector_store import get_vector_store_service; svc = get_vector_store_service()"
```

### Database Issues

```bash
# Check connection
python -c "from app.db.session import get_db_connection; import asyncio; asyncio.run(get_db_connection())"
```

### LLM Issues

- Verify API keys in `.env`
- Check model availability
- Review rate limits

## License

MIT

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request