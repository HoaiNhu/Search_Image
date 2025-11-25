"""
Script to monitor memory usage of the API
Run this to check if memory stays under 512MB
"""
import psutil
import time
import requests
from datetime import datetime

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024  # Convert to MB

def monitor_api(base_url="http://localhost:8001", duration=60):
    """
    Monitor API memory usage
    
    Args:
        base_url: Base URL of the API
        duration: How long to monitor (seconds)
    """
    print("=" * 60)
    print("Memory Monitor for Image Search API")
    print("=" * 60)
    print(f"Target: Keep under 512MB for Render free tier")
    print(f"Monitoring: {base_url}")
    print(f"Duration: {duration} seconds")
    print("=" * 60)
    
    # Initial memory
    initial_memory = get_memory_usage()
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Initial Memory: {initial_memory:.2f} MB")
    
    max_memory = initial_memory
    measurements = []
    
    try:
        start_time = time.time()
        test_count = 0
        
        while time.time() - start_time < duration:
            current_memory = get_memory_usage()
            max_memory = max(max_memory, current_memory)
            measurements.append(current_memory)
            
            # Print current status
            status = "✅ OK" if current_memory < 512 else "❌ OVER LIMIT"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Current: {current_memory:.2f} MB | Peak: {max_memory:.2f} MB | {status}")
            
            # Make a test request every 10 seconds
            if test_count % 2 == 0:
                try:
                    response = requests.get(f"{base_url}/api/v1/health", timeout=5)
                    print(f"  → Health check: {response.status_code}")
                except Exception as e:
                    print(f"  → Health check failed: {str(e)}")
            
            test_count += 1
            time.sleep(5)
        
        # Summary
        avg_memory = sum(measurements) / len(measurements)
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Initial Memory:  {initial_memory:.2f} MB")
        print(f"Average Memory:  {avg_memory:.2f} MB")
        print(f"Peak Memory:     {max_memory:.2f} MB")
        print(f"Memory Growth:   {max_memory - initial_memory:.2f} MB")
        print("=" * 60)
        
        if max_memory < 450:
            print("✅ EXCELLENT - Well under 512MB limit!")
        elif max_memory < 512:
            print("✅ GOOD - Under 512MB limit (but close)")
        else:
            print("❌ FAIL - Exceeds 512MB limit!")
            print("⚠️  Consider:")
            print("   - Set CACHE_PRODUCTS=false")
            print("   - Set LAZY_LOAD_MODEL=true")
            print("   - Reduce TOP_K")
            print("   - Upgrade Render plan")
        
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"\n\nError: {str(e)}")

if __name__ == "__main__":
    import sys
    
    # Check if psutil is installed
    try:
        import psutil
        import requests
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "requests"])
        import psutil
        import requests
    
    # Get URL from command line or use default
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    
    print("\nMake sure your API is running!")
    print("Start it with: cd src && python main.py\n")
    
    time.sleep(2)
    monitor_api(url, duration)
