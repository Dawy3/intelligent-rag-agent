"""
Document ingestion service
"""
import uuid
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import get_settings


class IngestionService:
    """Service for processing and ingestion documents"""
    
    def __init__(self):
        self.setting = get_settings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.setting.chunk_size,
            chunk_overlap = self.setting.chunk_overlap 
        )    
        
    async def process_pdf(self, file_path: str, filename: str):
        """Process a PDF file and return chunks with metadata"""
        # Load Document
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Split into  chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add metadata
        
        doc_id = str(uuid.uuid4())
        for chunk in chunks:
            chunk.metadata.update({
                "doc_id" : doc_id,
                "filename": filename
            })
            
        return {
            "doc_id" : doc_id,
            "chunks": chunks,
            "num_chunks": len(chunks)
        }
        
    def cleanup_temp_file(self, file_path:str):
        """Remove temporary file"""
        if os.path.exists(file_path):
            os.unlink(file_path)
            
            
def get_ingestion_service() -> IngestionService:
    """Get ingestion service instance"""
    return IngestionService()
        
    