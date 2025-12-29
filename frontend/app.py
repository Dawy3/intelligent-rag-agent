"""
Streamlit Frontend for Intelligent RAG Agent
"""
import streamlit as st
import requests
import os
from typing import List, Dict
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_BASE = f"{BACKEND_URL}/api/v1"

# Page configuration
st.set_page_config(
    page_title="Intelligent RAG Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []


def reset_chat():
    """Reset chat history"""
    st.session_state.messages = []
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def upload_document(file) -> Dict:
    """Upload document to backend"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(
            f"{API_BASE}/documents/upload",
            files=files,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error uploading document: {str(e)}")
        return None


def query_agent(query: str, session_id: str) -> Dict:
    """Query the RAG agent"""
    try:
        payload = {
            "query": query,
            "session_id": session_id
        }
        response = requests.post(
            f"{API_BASE}/agent/query",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error querying agent: {str(e)}")
        return None


def get_analytics() -> Dict:
    """Get analytics from backend"""
    try:
        response = requests.get(
            f"{API_BASE}/agent/analytics",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not fetch analytics: {str(e)}")
        return None


# Sidebar
with st.sidebar:
    st.title("🤖 Intelligent RAG Agent")
    st.markdown("---")
    
    # Document Upload Section
    st.subheader("📄 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a PDF document to add to the knowledge base"
    )
    
    if uploaded_file is not None:
        if st.button("Upload Document", use_container_width=True):
            with st.spinner("Uploading and processing document..."):
                result = upload_document(uploaded_file)
                if result:
                    st.success(f"✅ {result['filename']} uploaded successfully!")
                    st.info(f"📊 Created {result['chunks_created']} chunks")
                    st.session_state.uploaded_docs.append({
                        "filename": result['filename'],
                        "doc_id": result['doc_id'],
                        "chunks": result['chunks_created'],
                        "timestamp": datetime.now()
                    })
                    st.rerun()
    
    st.markdown("---")
    
    # Chat Management
    st.subheader("💬 Chat Management")
    if st.button("🆕 New Chat", use_container_width=True):
        reset_chat()
        st.rerun()
    
    st.markdown("---")
    
    # Analytics Section
    st.subheader("📊 Analytics")
    if st.button("Refresh Analytics", use_container_width=True):
        analytics = get_analytics()
        if analytics:
            st.session_state.analytics = analytics
    
    if "analytics" in st.session_state:
        analytics = st.session_state.analytics
        st.metric("Total Queries", analytics.get("total_queries", 0))
        st.metric("Avg Tools/Query", f"{analytics.get('avg_tools_per_query', 0):.2f}")
        
        if analytics.get("tool_usage"):
            st.markdown("**Tool Usage:**")
            for tool in analytics["tool_usage"]:
                st.text(f"• {tool['tool']}: {tool['count']}")
    
    st.markdown("---")
    
    # Uploaded Documents List
    if st.session_state.uploaded_docs:
        st.subheader("📚 Uploaded Documents")
        for doc in st.session_state.uploaded_docs:
            with st.expander(f"📄 {doc['filename']}"):
                st.text(f"ID: {doc['doc_id']}")
                st.text(f"Chunks: {doc['chunks']}")
                st.text(f"Uploaded: {doc['timestamp'].strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("---")
    
    # Session Info
    st.subheader("ℹ️ Session Info")
    st.text(f"Session ID:\n{st.session_state.session_id}")
    
    # Backend Status
    st.markdown("---")
    st.subheader("🔌 Backend Status")
    try:
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")


# Main Chat Interface
st.title("💬 Chat with RAG Agent")
st.markdown("Ask questions and get intelligent answers powered by RAG!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show metadata if available
        if message["role"] == "assistant" and "metadata" in message:
            metadata = message["metadata"]
            with st.expander("📊 Response Details"):
                if metadata.get("tool_used"):
                    st.markdown(f"**Tools Used:** {', '.join(metadata['tool_used'])}")
                if metadata.get("reasoning_steps"):
                    st.markdown(f"**Reasoning Steps:** {metadata['reasoning_steps']}")
                if metadata.get("sources"):
                    st.markdown(f"**Sources:** {len(metadata['sources'])}")

# Chat input
if prompt := st.chat_input("Ask a question..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_agent(prompt, st.session_state.session_id)
            
            if response:
                answer = response.get("answer", "No answer received")
                st.markdown(answer)
                
                # Store message with metadata
                metadata = {
                    "tool_used": response.get("tool_used", []),
                    "reasoning_steps": response.get("reasoning_steps", 0),
                    "sources": response.get("sources", [])
                }
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "metadata": metadata
                })
                
                # Show metadata
                with st.expander("📊 Response Details"):
                    if metadata["tool_used"]:
                        st.markdown(f"**Tools Used:** {', '.join(metadata['tool_used'])}")
                    st.markdown(f"**Reasoning Steps:** {metadata['reasoning_steps']}")
                    if metadata["sources"]:
                        st.markdown(f"**Sources:** {len(metadata['sources'])}")
            else:
                error_msg = "Sorry, I encountered an error processing your query. Please try again."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Intelligent RAG Agent v1.0.0 | Powered by LangChain & LangGraph"
    "</div>",
    unsafe_allow_html=True
)