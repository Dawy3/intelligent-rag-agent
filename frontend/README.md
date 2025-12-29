# Intelligent RAG Agent - Frontend

Streamlit-based frontend interface for the Intelligent RAG Agent.

## Features

- 📄 **Document Upload**: Upload PDF documents to add to the knowledge base
- 💬 **Chat Interface**: Interactive chat with the RAG agent
- 🆕 **New Chat**: Start fresh conversations
- 📊 **Analytics**: View usage statistics and tool usage
- 📚 **Document Management**: View uploaded documents and their metadata

## Setup

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export BACKEND_URL=http://localhost:8000
```

3. Run Streamlit:
```bash
streamlit run app.py
```

The frontend will be available at `http://localhost:8501`

### Docker

Build and run with Docker:

```bash
docker build -t rag-frontend .
docker run -p 8501:8501 -e BACKEND_URL=http://backend:8000 rag-frontend
```

## Configuration

- `BACKEND_URL`: Backend API URL (default: `http://backend:8000`)

## Integration

The frontend integrates with the backend API endpoints:

- `POST /api/v1/agent/query` - Query the RAG agent
- `POST /api/v1/documents/upload` - Upload documents
- `GET /api/v1/agent/analytics` - Get analytics
- `GET /health` - Health check

## UI Components

### Sidebar
- Document upload section
- Chat management (New Chat button)
- Analytics dashboard
- Uploaded documents list
- Session information
- Backend connection status

### Main Area
- Chat interface with message history
- Response metadata (tools used, reasoning steps, sources)
- Chat input for user queries

## Requirements

- Python 3.11+
- Streamlit 1.39.0+
- requests 2.32.3+

