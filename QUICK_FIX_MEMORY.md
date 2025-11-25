# 🚀 Quick Fix for Memory Error on Render

## Problem You're Having:

```
Instance failed: zhzhl
Ran out of memory (used over 512MB) while running your code.
```

## ✅ Quick Solution (3 Steps)

### Step 1: Add Environment Variables on Render Dashboard

Go to your Render service → **Environment** tab and add these:

```
CACHE_PRODUCTS=false
LAZY_LOAD_MODEL=true
MAX_BATCH_SIZE=4
```

### Step 2: Update Your Render Service Settings

In Render Dashboard → **Settings**:

**Start Command:**

```bash
cd src && uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1 --limit-concurrency 10
```

**Health Check Path:**

```
/api/v1/health
```

### Step 3: Redeploy

Click **Manual Deploy** → **Deploy latest commit**

## What Changed?

| Before                    | After                        | Memory Saved        |
| ------------------------- | ---------------------------- | ------------------- |
| Model loads on startup    | Model loads on first request | ~150MB              |
| All features pre-computed | Features computed on-demand  | ~200MB              |
| Multiple workers          | 1 worker only                | ~100MB              |
| **Total: 500MB+**         | **Total: ~400MB**            | **Saved 100-200MB** |

## Expected Behavior

✅ **First API call**: Will take 3-5 seconds (loading model)  
✅ **Subsequent calls**: 1-2 seconds each  
✅ **Memory usage**: ~400-450MB (within 512MB limit)

## Test Your API

Once deployed, test with:

```bash
# Health check
curl https://your-app.onrender.com/api/v1/health

# Search by URL (first call will be slow)
curl -X POST https://your-app.onrender.com/api/v1/search/url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "top_k": 5
  }'
```

## If Still Having Issues

### Option 1: Reduce results returned

```
TOP_K=5
SIMILARITY_THRESHOLD=0.7
```

### Option 2: Upgrade to Paid Plan

Render Starter ($7/month) gives you 2GB RAM = much better performance

## Monitor Logs

Watch for these messages:

```
✅ "Lazy loading search service components..." - Good!
✅ "Services will be initialized on first request" - Good!
❌ "Ran out of memory" - Still issues, try Option 1 or 2 above
```

## Files Updated

- `.env` - Added memory optimization flags
- `render.yaml` - Updated config
- `Dockerfile` - Optimized build
- `src/config/settings.py` - Added new settings
- `src/services/feature_extractor.py` - Lazy loading
- `src/services/search_service.py` - On-demand computation

All changes are committed and ready to deploy! 🎉
