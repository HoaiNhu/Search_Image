"""
API routes for image search endpoints.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse

from models.product import SearchResult
from services.search_service import get_search_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.post("/search/image", response_model=List[SearchResult])
async def search_by_image(
    file: UploadFile = File(...),
    top_k: Optional[int] = Query(None, ge=1, le=50, description="Number of results to return"),
    threshold: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum similarity threshold")
) -> List[SearchResult]:
    """
    Search for similar products by uploading an image.
    
    Args:
        file: Uploaded image file (JPEG, PNG, etc.)
        top_k: Number of top results to return (default: 10)
        threshold: Minimum similarity threshold (default: 0.5)
        
    Returns:
        List of similar products with similarity scores
        
    Raises:
        HTTPException: If image processing fails
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="Empty image file"
            )
        
        # Perform search
        search_service = get_search_service()
        results = search_service.search_by_image_bytes(
            image_bytes=image_bytes,
            top_k=top_k,
            threshold=threshold
        )
        
        logger.info(f"Image search completed: {len(results)} results found")
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_by_image endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/search/url")
async def search_by_url(
    image_url: str = Query(..., description="URL of the image to search"),
    top_k: Optional[int] = Query(None, ge=1, le=50, description="Number of results to return"),
    threshold: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum similarity threshold")
) -> List[SearchResult]:
    """
    Search for similar products using an image URL.
    
    Args:
        image_url: URL of the image to search
        top_k: Number of top results to return (default: 10)
        threshold: Minimum similarity threshold (default: 0.5)
        
    Returns:
        List of similar products with similarity scores
        
    Raises:
        HTTPException: If image processing fails
    """
    try:
        if not image_url:
            raise HTTPException(
                status_code=400,
                detail="Image URL is required"
            )
        
        # Perform search
        search_service = get_search_service()
        results = search_service.search_by_image_url(
            image_url=image_url,
            top_k=top_k,
            threshold=threshold
        )
        
        logger.info(f"URL search completed: {len(results)} results found")
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_by_url endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/refresh")
async def refresh_product_features() -> JSONResponse:
    """
    Refresh product features from database.
    This endpoint should be called when products are updated.
    
    Returns:
        Success message
    """
    try:
        search_service = get_search_service()
        search_service.refresh_product_features()
        
        logger.info("Product features refreshed successfully")
        return JSONResponse(
            status_code=200,
            content={
                "message": "Product features refreshed successfully",
                "total_products": len(search_service.products),
                "indexed_products": len(search_service.product_features)
            }
        )
    except Exception as e:
        logger.error(f"Error in refresh endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh product features: {str(e)}"
        )


@router.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint.
    Does NOT initialize search service to avoid loading model.
    
    Returns:
        Service health status
    """
    try:
        # Don't initialize search service - just check if API is running
        # This avoids loading the model during health checks
        from services.database import get_database_service
        
        # Just check database connection
        db_service = get_database_service()
        db_healthy = db_service is not None
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "message": "API is running",
                "database": "connected" if db_healthy else "disconnected",
                "note": "Model will load on first search request"
            }
        )
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@router.get("/status")
async def detailed_status() -> JSONResponse:
    """
    Detailed status endpoint - shows if model is loaded.
    Use this AFTER first search to check system status.
    
    Returns:
        Detailed service status
    """
    try:
        search_service = get_search_service()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "model_loaded": search_service._initialized if hasattr(search_service, '_initialized') else False,
                "total_products": len(search_service.products),
                "cached_features": len(search_service.product_features),
                "cache_enabled": search_service.product_features is not None and len(search_service.product_features) > 0
            }
        )
    except Exception as e:
        logger.error(f"Error in status check: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "error": str(e)
            }
        )
