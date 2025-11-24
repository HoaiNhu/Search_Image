"""
Keep-alive script to prevent Render free tier from sleeping.
This script pings the API every 10 minutes.
Run this on a separate server or use a cron service like cron-job.org
"""
import requests
import time
import os
from datetime import datetime

# Your Render API URL
API_URL = os.getenv("API_URL", "https://image-search-api.onrender.com")
PING_INTERVAL = 600  # 10 minutes in seconds

def ping_api():
    """Ping the API health endpoint"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=30)
        if response.status_code == 200:
            print(f"[{datetime.now()}] ✅ API is healthy: {response.json()}")
            return True
        else:
            print(f"[{datetime.now()}] ⚠️ API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] ❌ Error pinging API: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"🚀 Starting keep-alive service for {API_URL}")
    print(f"⏰ Ping interval: {PING_INTERVAL // 60} minutes")
    print("-" * 50)
    
    while True:
        ping_api()
        time.sleep(PING_INTERVAL)
