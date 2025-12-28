# Project Structure

Complete file structure for the Intelligent RAG Agent project.

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   │                              # - Creates FastAPI app
│   │                              # - Sets up CORS, middleware
│   │                              # - Includes routers
│   │                              # - Defines lifecycle events
│   │
│   ├── config.py                  # Application configuration
│   │                              # - Pydantic Settings for env vars
│   │                              # - All configurable parameters
│   │                              # - Cached settings instance
│   │
│   ├── api/                       # HTTP API layer (thin controllers)
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── routes.py          # API endpoints
│   │       │                      # - POST /agent/query
│   │       │                      # - POST /documents/upload
│   │       │                      # - GET /agent/analytics
│   │       │
│   │       └── schemas.py         # Request/Response models
│   │                              # - QueryRequest/Response
│   │                              # - DocumentUploadResponse
│   │                              # - AnalyticsResponse
│   │
│   ├── core/                      # AI/Agent logic (business brain)
│   │   ├── __init__.py
│   │   ├── agents.py              # Tool definitions
│   │   │                          # - @tool decorated functions
│   │   │                          # - search_knowledge_base
│   │   │                          # - search_web
│   │   │                          # - calculate
│   │   │
│   │   ├── graph.py               # LangGraph workflow
│   │   │                          # - Agent node (reasoning)
│   │   │                          # - Tool node (execution)
│   │   │                          # - Router (decision logic)
│   │   │                          # - Graph compilation
│   │   │
│   │   ├── prompts.py             # System prompts & templates
│   │   │                          # - Agent instructions
│   │   │                          # - Tool usage guidelines
│   │   │
│   │   └── state.py               # Agent state definition
│   │                              # - AgentState TypedDict
│   │                              # - Message history
│   │                              # - Metadata tracking
│   │
│   ├── services/                  # External integrations
│   │   ├── __init__.py
│   │   ├── llm.py                 # LLM service
│   │   │                          # - ChatOpenAI initialization
│   │   │                          # - Tool binding
│   │   │
│   │   ├── vector_store.py        # Vector database service
│   │   │                          # - Pinecone initialization
│   │   │                          # - Embedding management
│   │   │                          # - Similarity search
│   │   │                          # - Document storage
│   │   │
│   │   └── ingestion.py           # Document processing
│   │                              # - PDF loading
│   │                              # - Text splitting
│   │                              # - Metadata enrichment
│   │
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── models.py              # Database models/schemas
│   │   │                          # - agent_queries table
│   │   │                          # - agent_tool_usage table
│   │   │
│   │   └── session.py             # Database connections
│   │                              # - Connection factory
│   │                              # - Table creation
│   │
│   └── utils/                     # Helper utilities
│       ├── __init__.py
│       └── logging.py             # Logging configuration
│                                  # - Logger setup
│                                  # - Formatter configuration
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_agents.py
│   └── test_services.py
│
├── .env                           # Environment variables (DO NOT COMMIT)
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker image definition
├── docker-compose.yml             # Multi-container setup
├── Makefile                       # Common commands
├── run.sh                         # Startup script
└── README.md                      # Documentation
```

## File Responsibilities

### Core Application Files

**`main.py`**
- Entry point for the application
- FastAPI app initialization
- Middleware configuration
- Router registration
- Lifecycle management (startup/shutdown)

**`config.py`**
- Centralized configuration management
- Environment variable loading
- Default value definitions
- Settings validation

### API Layer (`api/v1/`)

**`routes.py`**
- HTTP endpoint definitions
- Request validation
- Response formatting
- Business logic orchestration
- Error handling

**`schemas.py`**
- Pydantic models for validation
- Request/response structure
- Data serialization
- Type definitions

### Core AI Logic (`core/`)

**`agents.py`**
- Custom tool implementations
- Tool registration
- Tool node creation
- Business-specific logic

**`graph.py`**
- LangGraph workflow definition
- Agent reasoning logic
- Routing decisions
- State management
- Graph compilation

**`prompts.py`**
- System prompts
- Agent instructions
- Behavior guidelines
- Reusable templates

**`state.py`**
- Agent state structure
- Message history
- Metadata tracking
- Type definitions

### Services Layer (`services/`)

**`llm.py`**
- LLM client initialization
- Model configuration
- Tool binding
- Request formatting

**`vector_store.py`**
- Vector database management
- Embedding generation
- Similarity search
- Document storage/retrieval

**`ingestion.py`**
- Document loading
- Text chunking
- Metadata enrichment
- File processing

### Database Layer (`db/`)

**`models.py`**
- Database schema definitions
- ORM models (if using SQLAlchemy)
- Table structures
- Relationships

**`session.py`**
- Database connection management
- Connection pooling
- Transaction handling
- Table initialization

### Utilities (`utils/`)

**`logging.py`**
- Logging configuration
- Log formatting
- Log level management
- Logger factory

## Data Flow

```
Request → routes.py → graph.py → agents.py → services/
                                       ↓
                                  vector_store.py
                                  llm.py
                                       ↓
Response ← routes.py ← graph.py ← agents.py
```

## Key Design Patterns

1. **Dependency Injection**: Services injected via factory functions
2. **Separation of Concerns**: Clear boundaries between layers
3. **Single Responsibility**: Each file has one clear purpose
4. **Configuration Management**: Centralized in config.py
5. **Service Layer**: External dependencies isolated
6. **Async/Await**: Throughout for performance

## Adding New Features

### New Tool
1. Define in `core/agents.py`
2. Add to `get_tools()` list
3. Update prompts if needed

### New Endpoint
1. Define schema in `api/v1/schemas.py`
2. Implement route in `api/v1/routes.py`
3. Update documentation

### New Service
1. Create new file in `services/`
2. Define service class
3. Create factory function
4. Use in routes or agents

## Configuration Flow

```
.env → config.py → services/ → core/ → api/
```

All configuration flows through `config.py` using Pydantic Settings.