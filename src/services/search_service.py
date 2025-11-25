"""
Image search service for finding similar products.
"""
import gc
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from config.settings import config
from models.product import SearchResult, Product
from services.database import get_database_service
from services.feature_extractor import get_feature_extractor

logger = logging.getLogger(__name__)


class SearchService:
    """Service for performing image-based product search."""
    
    def __init__(self):
        """Initialize search service."""
        self.db_service = None
        self.feature_extractor = None
        self.product_features: Dict[str, np.ndarray] = {}
        self.products: List[Dict[str, Any]] = []
        self._initialized = False
    
    def _ensure_initialized(self) -> None:
        """Lazy initialization - only load when needed."""
        if self._initialized:
            return
        
        logger.info("Lazy loading search service components...")
        self.db_service = get_database_service()
        self.feature_extractor = get_feature_extractor()
        
        # Only pre-compute features if caching is enabled
        if config.CACHE_PRODUCTS:
            self._initialize_product_features()
        else:
            logger.info("Product feature caching disabled - will compute on-demand")
            # Load limited products to reduce memory
            max_products = config.MAX_PRODUCTS if hasattr(config, 'MAX_PRODUCTS') else None
            self.products = self.db_service.get_products_with_images(limit=max_products)
            logger.info(f"Loaded {len(self.products)} products (limit: {max_products})")
        
        self._initialized = True
    
    def _initialize_product_features(self) -> None:
        """Pre-compute features for all products in database."""
        try:
            logger.info("Initializing product features...")
            # Limit products to reduce memory
            max_products = config.MAX_PRODUCTS if hasattr(config, 'MAX_PRODUCTS') else None
            self.products = self.db_service.get_products_with_images(limit=max_products)
            
            if not self.products:
                logger.warning("No products with images found in database")
                return
            
            success_count = 0
            for product in self.products:
                product_id = str(product.get('_id'))
                image_url = product.get('productImage')
                
                if not image_url:
                    continue
                
                # Extract features
                features = self.feature_extractor.extract_features_from_url(image_url)
                
                if features is not None:
                    self.product_features[product_id] = features
                    success_count += 1
                    logger.debug(f"Extracted features for product {product_id}")
            
            logger.info(f"Successfully extracted features for {success_count}/{len(self.products)} products")
        except Exception as e:
            logger.error(f"Error initializing product features: {str(e)}")
    
    def search_by_image_bytes(
        self, 
        image_bytes: bytes, 
        top_k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """
        Search for similar products using uploaded image bytes.
        
        Args:
            image_bytes: Image data in bytes
            top_k: Number of top results to return (default from config)
            threshold: Minimum similarity threshold (default from config)
            
        Returns:
            List of SearchResult objects sorted by similarity
        """
        try:
            # Ensure services are initialized
            self._ensure_initialized()
            
            # Use defaults if not provided
            if top_k is None:
                top_k = config.TOP_K
            if threshold is None:
                threshold = config.SIMILARITY_THRESHOLD
            
            # Extract features from query image
            query_features = self.feature_extractor.extract_features_from_bytes(image_bytes)
            
            if query_features is None:
                logger.error("Failed to extract features from query image")
                return []
            
            # Calculate similarities
            results = self._calculate_similarities(query_features, top_k, threshold)
            
            return results
        except Exception as e:
            logger.error(f"Error in search_by_image_bytes: {str(e)}")
            return []
    
    def search_by_image_url(
        self, 
        image_url: str, 
        top_k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[SearchResult]:
        """
        Search for similar products using image URL.
        
        Args:
            image_url: URL of the query image
            top_k: Number of top results to return (default from config)
            threshold: Minimum similarity threshold (default from config)
            
        Returns:
            List of SearchResult objects sorted by similarity
        """
        try:
            # Ensure services are initialized
            self._ensure_initialized()
            
            # Use defaults if not provided
            if top_k is None:
                top_k = config.TOP_K
            if threshold is None:
                threshold = config.SIMILARITY_THRESHOLD
            
            # Extract features from query image
            query_features = self.feature_extractor.extract_features_from_url(image_url)
            
            if query_features is None:
                logger.error("Failed to extract features from query image URL")
                return []
            
            # Calculate similarities
            results = self._calculate_similarities(query_features, top_k, threshold)
            
            return results
        except Exception as e:
            logger.error(f"Error in search_by_image_url: {str(e)}")
            return []
    
    def _calculate_similarities(
        self, 
        query_features: np.ndarray, 
        top_k: int,
        threshold: float
    ) -> List[SearchResult]:
        """
        Calculate similarity scores between query and all products.
        
        Args:
            query_features: Feature vector of query image
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of SearchResult objects sorted by similarity
        """
        try:
            # If caching is disabled, compute features on-demand
            if not config.CACHE_PRODUCTS:
                return self._calculate_similarities_on_demand(query_features, top_k, threshold)
            
            if not self.product_features:
                logger.warning("No product features available for comparison")
                return []
            
            similarities = []
            
            # Calculate cosine similarity for each product
            for product_id, product_features in self.product_features.items():
                similarity = cosine_similarity(
                    query_features.reshape(1, -1),
                    product_features.reshape(1, -1)
                )[0][0]
                
                # Apply threshold
                if similarity >= threshold:
                    similarities.append({
                        'product_id': product_id,
                        'similarity': float(similarity)
                    })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Take top K
            top_similarities = similarities[:top_k]
            
            # Create SearchResult objects
            results = []
            for rank, item in enumerate(top_similarities, start=1):
                product_id = item['product_id']
                similarity = item['similarity']
                
                # Find product data
                product_data = next(
                    (p for p in self.products if str(p.get('_id')) == product_id),
                    None
                )
                
                if product_data:
                    # Convert MongoDB document to Product model
                    product = Product(**product_data)
                    
                    result = SearchResult(
                        product=product,
                        similarity_score=similarity,
                        rank=rank
                    )
                    results.append(result)
            
            logger.info(f"Found {len(results)} similar products (threshold: {threshold})")
            return results
        except Exception as e:
            logger.error(f"Error calculating similarities: {str(e)}")
            return []
    
    def _calculate_similarities_on_demand(
        self, 
        query_features: np.ndarray, 
        top_k: int,
        threshold: float
    ) -> List[SearchResult]:
        """
        Calculate similarities by computing product features on-demand.
        This uses less memory but is slower than pre-computed features.
        """
        try:
            if not self.products:
                logger.warning("No products available")
                return []
            
            similarities = []
            
            # Compute features on-demand for each product
            for product in self.products:
                product_id = str(product.get('_id'))
                image_url = product.get('productImage')
                
                if not image_url:
                    continue
                
                # Extract features on-the-fly
                product_features = self.feature_extractor.extract_features_from_url(image_url)
                
                if product_features is None:
                    continue
                
                # Calculate similarity
                similarity = cosine_similarity(
                    query_features.reshape(1, -1),
                    product_features.reshape(1, -1)
                )[0][0]
                
                # Apply threshold
                if similarity >= threshold:
                    similarities.append({
                        'product_id': product_id,
                        'product_data': product,
                        'similarity': float(similarity)
                    })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Take top K
            top_similarities = similarities[:top_k]
            
            # Create SearchResult objects
            results = []
            for rank, item in enumerate(top_similarities, start=1):
                product = Product(**item['product_data'])
                result = SearchResult(
                    product=product,
                    similarity_score=item['similarity'],
                    rank=rank
                )
                results.append(result)
            
            logger.info(f"Found {len(results)} similar products using on-demand computation")
            
            # Force garbage collection if enabled
            if config.ENABLE_GC:
                gc.collect()
            
            return results
        except Exception as e:
            logger.error(f"Error in on-demand similarity calculation: {str(e)}")
            return []
    
    def refresh_product_features(self) -> None:
        """Refresh product features from database."""
        logger.info("Refreshing product features...")
        self._ensure_initialized()
        self.product_features.clear()
        self.products.clear()
        self._initialize_product_features()


# Singleton instance
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """
    Get or create search service instance.
    
    Returns:
        SearchService instance
    """
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
