"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api.v1.routes import router as v1_router
from app.db.session import create_tables
from app.utils.logging import setup_logging, get_logger


@asynccontextmanager
async def lifespan(app:FastAPI):
    """Lifecycle events"""
    # Startup
    logger = get_logger(__name__)
    logger.info("Starting application...")
    
    # Initialize database tables
    try:
        await create_tables()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.warning(f"Could not create database tables: {e}")
        
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    

def create_app()-> FastAPI:
    """Create and configure fastapi application"""
    
    # Setup logging
    setup_logging()
    
    settings = get_settings()
    
    # Create FASTAPI app
    app = FastAPI(
        title=  settings.app_title,
        version= settings.app_version,
        lifespan= lifespan
    )
    
    
    # Add CROS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(v1_router, prefix="/api/v1", tags=["v1"])
        
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Intelligent RAG Agent API",
            "version": settings.app_version,
            "status": "running"
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {"status": "healthy"}
    
    return app


# Create app instance
app = create_app()