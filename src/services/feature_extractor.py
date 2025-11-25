"""
Image feature extraction service using CLIP model.
"""
import gc
import logging
from typing import Optional, List
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

from config.settings import config
from utils.image_utils import ImageProcessor

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
        self._model_loaded = False
        
        # Only load immediately if not using lazy loading
        if not config.LAZY_LOAD_MODEL:
            self._load_model()
    
    def _load_model(self) -> None:
        """Load CLIP model and processor."""
        if self._model_loaded:
            return
            
        try:
            logger.info(f"Loading CLIP model: {self.model_name}")
            # Use low_cpu_mem_usage to reduce memory footprint during loading
            self.model = CLIPModel.from_pretrained(
                self.model_name,
                low_cpu_mem_usage=True,
                torch_dtype=torch.float32  # Use float32 for CPU
            )
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            # Enable memory efficient inference
            if hasattr(torch, 'inference_mode'):
                torch.set_grad_enabled(False)
            
            self._model_loaded = True
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
            # Ensure model is loaded
            if not self._model_loaded:
                self._load_model()
            
            # Process image
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Extract features with memory efficient inference
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            
            # Normalize features
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy and clear GPU memory if needed
            features = image_features.cpu().numpy().flatten()
            
            # Clean up tensors
            del inputs, image_features
            if self.device != "cpu":
                torch.cuda.empty_cache()
            
            # Force garbage collection if enabled
            if config.ENABLE_GC:
                gc.collect()
            
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
