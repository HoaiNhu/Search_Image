"""
Image feature extraction service using CLIP model.
"""
import logging
from typing import Optional, List
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

from config import config
from utils import ImageProcessor

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Service for extracting image features using CLIP model."""
    
    def __init__(self):
        """Initialize CLIP model and processor."""
        self.device = config.DEVICE
        self.model_name = config.MODEL_NAME
        self.model: Optional[CLIPModel] = None
        self.processor: Optional[CLIPProcessor] = None
        self.image_processor = ImageProcessor()
        self._load_model()
    
    def _load_model(self) -> None:
        """Load CLIP model and processor."""
        try:
            logger.info(f"Loading CLIP model: {self.model_name}")
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"CLIP model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Error loading CLIP model: {str(e)}")
            raise
    
    def extract_features_from_image(self, image: Image.Image) -> Optional[np.ndarray]:
        """
        Extract features from a PIL Image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Feature vector as numpy array or None if failed
        """
        try:
            # Process image
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Extract features
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            
            # Normalize features
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy
            features = image_features.cpu().numpy().flatten()
            
            return features
        except Exception as e:
            logger.error(f"Error extracting features from image: {str(e)}")
            return None
    
    def extract_features_from_url(self, image_url: str) -> Optional[np.ndarray]:
        """
        Extract features from an image URL.
        
        Args:
            image_url: URL of the image
            
        Returns:
            Feature vector as numpy array or None if failed
        """
        try:
            # Download image
            image = self.image_processor.download_image(image_url)
            if image is None:
                return None
            
            # Extract features
            return self.extract_features_from_image(image)
        except Exception as e:
            logger.error(f"Error extracting features from URL {image_url}: {str(e)}")
            return None
    
    def extract_features_from_bytes(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Extract features from image bytes.
        
        Args:
            image_bytes: Image data in bytes
            
        Returns:
            Feature vector as numpy array or None if failed
        """
        try:
            # Load image from bytes
            image = self.image_processor.load_image_from_bytes(image_bytes)
            if image is None:
                return None
            
            # Extract features
            return self.extract_features_from_image(image)
        except Exception as e:
            logger.error(f"Error extracting features from bytes: {str(e)}")
            return None
    
    def extract_batch_features(self, images: List[Image.Image]) -> Optional[np.ndarray]:
        """
        Extract features from multiple images in batch.
        
        Args:
            images: List of PIL Image objects
            
        Returns:
            Feature matrix as numpy array (N x D) or None if failed
        """
        try:
            if not images:
                return None
            
            # Process batch
            inputs = self.processor(images=images, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Extract features
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            
            # Normalize features
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy
            features = image_features.cpu().numpy()
            
            return features
        except Exception as e:
            logger.error(f"Error extracting batch features: {str(e)}")
            return None


# Singleton instance
_feature_extractor: Optional[FeatureExtractor] = None


def get_feature_extractor() -> FeatureExtractor:
    """
    Get or create feature extractor instance.
    
    Returns:
        FeatureExtractor instance
    """
    global _feature_extractor
    if _feature_extractor is None:
        _feature_extractor = FeatureExtractor()
    return _feature_extractor
