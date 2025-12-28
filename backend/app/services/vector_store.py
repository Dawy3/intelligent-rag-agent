"""
Vector store service for document embeddings and search
"""
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from app.config import get_settings


class VectorStoreService:
    """Service for managing vector store operations"""
    
    def __init__(self):
        self.setting = get_settings()
        self.embeddings = self._initialize_embedding()
        self.pc = Pinecone(api_key=self.setting.pinecone_api_key)
        self._ensure_index_exists()
        self.vectorstore = self._initialize_vectorstore()
        
    def _initialize_embedding(self):
        """Initialize HugingFace Embedding"""
        return HuggingFaceEmbeddings(
            model_name = self.setting.embedding_model_name,
            model_kwargs = {'device': self.setting.embedding_device},
            encode_kwargs = {'normalize_embedding': True}
        )
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exists"""
        if self.setting.pinecone_index_name not in self.pc.list_indexes().names():
            # Get dimension from sample embedding
            sample_embedding = self.embeddings.embed_query("test")
            dimension = len(sample_embedding)
            
            self.pc.create_index(
                name= self.setting.pinecone_index_name,
                dimension= dimension,
                metric = self.setting.pinecone_metric,
                spec= ServerlessSpec(
                    cloud = self.setting.pinecone_cloud,
                    region= self.setting.pinecone_region
                )
            )
            
    def _initialize_vectorstore(self):
        """Initialize Pinecone vector store"""
        return PineconeVectorStore(
            index_name= self.setting.pinecone_index_name,
            embedding=self.embeddings
        )
    
        
    async def add_documents(self, documents):
        """Add documents to vector store"""
        return await self.vectorstore.add_documents(documents)    
    
    
    async def similarity_search(self, query:str, k:int = None):
        """Perform similarity search"""
        k = k or self.setting.similarity_search_k
        return await self.vectorstore.asimilarity_search(query , k=k)
    
    
# Global instance
_vector_store_service= None

def get_vector_store_service() -> VectorStoreService:
    """Get or create vector store service instance"""
    global _vector_store_service
    if _vector_store_service is None:
        _vector_store_service = VectorStoreService()
    
    return _vector_store_service
    
# You can also use lru-cash instead
"""
@lru_cache()
def get_vector_store_service():
    return VectorStoreService()
"""