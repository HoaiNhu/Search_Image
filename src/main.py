"""
Main application entry point for the image search API.
"""
import logging
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import config
from src.api.routes import router
from src.utils.logger import setup_logger

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Image Search API...")
    config.validate()
    logger.info(f"Configuration validated successfully")
    
    # Initialize services (lazy loading on first request)
    from src.services.search_service import get_search_service
    logger.info("Initializing search service...")
    get_search_service()
    logger.info("Search service initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Image Search API...")


# Create FastAPI application
app = FastAPI(
    title="Image Search API",
    description="API for searching products by image similarity using CLIP model",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Image Search API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/v1/health",
            "search_by_image": "/api/v1/search/image",
            "search_by_url": "/api/v1/search/url",
            "refresh": "/api/v1/refresh",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {config.HOST}:{config.PORT}")
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )
