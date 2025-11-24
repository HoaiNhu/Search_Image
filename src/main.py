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
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config.settings import config
from api.routes import router
from utils.logger import setup_logger

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
    logger.info("Services will be initialized on first request (lazy loading)")
    
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
