"""
Entry point for running the image search API.
Run this file from the root directory: python run.py
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    from src.config.settings import config
    
    print(f"Starting Image Search API on {config.HOST}:{config.PORT}")
    print(f"Documentation: http://{config.HOST}:{config.PORT}/docs")
    
    uvicorn.run(
        "src.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )
