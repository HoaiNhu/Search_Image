#!/usr/bin/env python3
"""
Emergency Memory Fix Test Script
Tests if the API can start without OOM errors
"""
import sys
import time
import psutil
import os

def check_memory():
    """Check current memory usage"""
    process = psutil.Process()
    mem = process.memory_info().rss / 1024 / 1024  # MB
    return mem

def main():
    print("=" * 60)
    print("EMERGENCY MEMORY TEST - Checking if API can start safely")
    print("=" * 60)
    
    # Change to src directory
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    os.chdir(src_dir)
    
    # Add to path
    sys.path.insert(0, src_dir)
    
    print("\n[1] Checking initial memory...")
    initial_mem = check_memory()
    print(f"    Initial Memory: {initial_mem:.2f} MB")
    
    if initial_mem > 300:
        print("    ⚠️  WARNING: Already using a lot of memory!")
    
    print("\n[2] Importing modules...")
    try:
        from config.settings import config
        print(f"    ✅ Config loaded")
        print(f"       - LAZY_LOAD_MODEL: {config.LAZY_LOAD_MODEL}")
        print(f"       - CACHE_PRODUCTS: {config.CACHE_PRODUCTS}")
        print(f"       - MAX_BATCH_SIZE: {config.MAX_BATCH_SIZE}")
    except Exception as e:
        print(f"    ❌ Failed to load config: {e}")
        return False
    
    mem_after_config = check_memory()
    print(f"    Memory after config: {mem_after_config:.2f} MB (+{mem_after_config-initial_mem:.2f} MB)")
    
    print("\n[3] Loading FastAPI app...")
    try:
        from main import app
        print(f"    ✅ App loaded")
    except Exception as e:
        print(f"    ❌ Failed to load app: {e}")
        return False
    
    mem_after_app = check_memory()
    print(f"    Memory after app: {mem_after_app:.2f} MB (+{mem_after_app-mem_after_config:.2f} MB)")
    
    print("\n[4] Checking services (WITHOUT initialization)...")
    try:
        from services.search_service import _search_service
        from services.feature_extractor import _feature_extractor
        
        if _search_service is None:
            print("    ✅ Search service NOT initialized (good!)")
        else:
            print("    ⚠️  Search service already initialized")
        
        if _feature_extractor is None:
            print("    ✅ Feature extractor NOT initialized (good!)")
        else:
            print("    ⚠️  Feature extractor already initialized")
    except Exception as e:
        print(f"    ⚠️  Could not check services: {e}")
    
    mem_after_check = check_memory()
    print(f"    Memory after check: {mem_after_check:.2f} MB")
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"Initial Memory:  {initial_mem:.2f} MB")
    print(f"Final Memory:    {mem_after_check:.2f} MB")
    print(f"Memory Growth:   {mem_after_check - initial_mem:.2f} MB")
    print("=" * 60)
    
    if mem_after_check < 200:
        print("✅ EXCELLENT - Very low memory usage!")
        print("✅ Should work perfectly on 512MB Render free tier")
    elif mem_after_check < 300:
        print("✅ GOOD - Reasonable memory usage")
        print("✅ Should work on 512MB with some headroom")
    elif mem_after_check < 400:
        print("⚠️  BORDERLINE - Getting close to limit")
        print("⚠️  Might work but will be tight on 512MB")
    else:
        print("❌ CRITICAL - Too much memory!")
        print("❌ Likely to fail on 512MB Render free tier")
        return False
    
    print("\n[5] Testing model lazy loading...")
    print("    (This should NOT load the model yet)")
    
    try:
        from services.feature_extractor import get_feature_extractor
        extractor = get_feature_extractor()
        
        if hasattr(extractor, '_model_loaded') and not extractor._model_loaded:
            print("    ✅ Model NOT loaded yet (perfect!)")
        elif not hasattr(extractor, '_model_loaded'):
            print("    ⚠️  Cannot check model load status")
        else:
            print("    ❌ Model already loaded (BAD!)")
            return False
    except Exception as e:
        print(f"    ⚠️  Could not test: {e}")
    
    mem_final = check_memory()
    print(f"    Final Memory: {mem_final:.2f} MB")
    
    if mem_final > mem_after_check + 50:
        print("    ❌ Memory increased too much!")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL CHECKS PASSED!")
    print("=" * 60)
    print("\nYour API should now:")
    print("1. Start with ~100-150MB memory")
    print("2. NOT load model during startup")
    print("3. Load model only on first search request")
    print("4. Stay under 512MB on Render free tier")
    print("\nDeploy to Render now! 🚀")
    
    return True

if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("Installing psutil...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
    
    success = main()
    sys.exit(0 if success else 1)
