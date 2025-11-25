"""
MongoDB database service for managing product data.
"""
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import logging

from config.settings import config
from models.product import Product

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for MongoDB database operations."""
    
    def __init__(self):
        """Initialize database connection."""
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self._collection: Optional[Collection] = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            self._client = MongoClient(config.MONGO_URI)
            self._db = self._client[config.MONGO_DB_NAME]
            self._collection = self._db[config.MONGO_COLLECTION]
            
            # Test connection
            self._client.server_info()
            logger.info(f"Connected to MongoDB: {config.MONGO_DB_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Retrieve all products from database.
        
        Returns:
            List of product documents
        """
        try:
            products = list(self._collection.find({}))
            logger.info(f"Retrieved {len(products)} products from database")
            return products
        except Exception as e:
            logger.error(f"Error retrieving products: {str(e)}")
            return []
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product document or None
        """
        try:
            from bson import ObjectId
            product = self._collection.find_one({"_id": ObjectId(product_id)})
            return product
        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {str(e)}")
            return None
    
    def get_products_with_images(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve products that have valid image URLs.
        
        Args:
            limit: Maximum number of products to retrieve (None for all)
            
        Returns:
            List of products with images
        """
        try:
            query = {
                "productImage": {"$exists": True, "$ne": None, "$ne": ""}
            }
            
            if limit:
                products = list(self._collection.find(query).limit(limit))
                logger.info(f"Retrieved {len(products)} products with images (limited to {limit})")
            else:
                products = list(self._collection.find(query))
                logger.info(f"Retrieved {len(products)} products with images")
            
            return products
        except Exception as e:
            logger.error(f"Error retrieving products with images: {str(e)}")
            return []
    
    def close(self) -> None:
        """Close database connection."""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")


# Singleton instance
_db_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """
    Get or create database service instance.
    
    Returns:
        DatabaseService instance
    """
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
