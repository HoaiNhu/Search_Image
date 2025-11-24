"""
Entry point for running the image search API.
Run this file from the root directory: python run.py
"""
import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

if __name__ == "__main__":
    import uvicorn
    from config.settings import config
    
    # Use PORT from environment variable (Render) or config
    port = int(os.environ.get('PORT', config.PORT))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Starting Image Search API on {host}:{port}")
    print(f"Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
