"""
Image utilities for processing and downloading images.
"""
import io
import logging
from typing import Optional
from PIL import Image
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Utility class for image processing operations."""
    
    def __init__(self):
        """Initialize image processor with retry strategy."""
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def download_image(self, image_url: str, timeout: int = 10) -> Optional[Image.Image]:
        """
        Download image from URL.
        
        Args:
            image_url: URL of the image
            timeout: Request timeout in seconds
            
        Returns:
            PIL Image object or None if failed
        """
        try:
            response = self.session.get(image_url, timeout=timeout)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            logger.error(f"Error downloading image from {image_url}: {str(e)}")
            return None
    
    def load_image_from_bytes(self, image_bytes: bytes) -> Optional[Image.Image]:
        """
        Load image from bytes.
        
        Args:
            image_bytes: Image data in bytes
            
        Returns:
            PIL Image object or None if failed
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            logger.error(f"Error loading image from bytes: {str(e)}")
            return None
    
    def resize_image(self, image: Image.Image, max_size: tuple = (512, 512)) -> Image.Image:
        """
        Resize image while maintaining aspect ratio.
        
        Args:
            image: PIL Image object
            max_size: Maximum dimensions (width, height)
            
        Returns:
            Resized PIL Image object
        """
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    
    def close(self):
        """Close the session."""
        self.session.close()
