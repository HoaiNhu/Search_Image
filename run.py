"""
Entry point for running the image search API.
Run this file from the root directory: python run.py
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    import uvicorn
    from config import config
    
    print(f"Starting Image Search API on {config.HOST}:{config.PORT}")
    print(f"Documentation: http://{config.HOST}:{config.PORT}/docs")
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )
