"""
Configuration module for the image search application.
Loads environment variables and provides configuration settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class."""
    
    # MongoDB Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "test")
    MONGO_COLLECTION: str = os.getenv("MONGO_COLLECTION", "products")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8001))
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "openai/clip-vit-base-patch32")
    DEVICE: str = os.getenv("DEVICE", "cpu")
    
    # Search Configuration
    TOP_K: int = int(os.getenv("TOP_K", 10))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", 0.5))
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.MONGO_URI:
            raise ValueError("MONGO_URI is required in environment variables")
        if not cls.MONGO_DB_NAME:
            raise ValueError("MONGO_DB_NAME is required in environment variables")


config = Config()
