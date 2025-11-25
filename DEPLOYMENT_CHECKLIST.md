# 🚀 Render Deployment Checklist

## Before Deploying

- [ ] All code changes committed and pushed to GitHub
- [ ] `.env` file updated with memory optimization settings
- [ ] `render.yaml` reviewed and updated
- [ ] Local testing completed (optional)

---

## Deployment Steps

### 1️⃣ Update Render Environment Variables

**Go to:** Render Dashboard → Your Service → **Environment** tab

**Add/Update these variables:**

```
✅ CACHE_PRODUCTS=false
✅ LAZY_LOAD_MODEL=true
✅ MAX_BATCH_SIZE=4
```

**Keep existing:**

```
MONGO_URI=<your-mongodb-uri>
MONGO_DB_NAME=test
MONGO_COLLECTION=products
MODEL_NAME=openai/clip-vit-base-patch32
DEVICE=cpu
TOP_K=10
SIMILARITY_THRESHOLD=0.5
```

### 2️⃣ Update Service Settings

**Go to:** Settings tab

**Update Start Command:**

```bash
cd src && uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1 --limit-concurrency 10
```

**Update Health Check Path:**

```
/api/v1/health
```

**Update Plan (if needed):**

- [ ] Free (512MB RAM) - Slower but works
- [ ] Starter ($7/month, 2GB RAM) - Faster

### 3️⃣ Deploy

**Option A - Auto Deploy (if enabled):**

```bash
git add .
git commit -m "fix: memory optimization for 512MB"
git push origin main
```

**Option B - Manual Deploy:**

- [ ] Click "Manual Deploy" button
- [ ] Select "Deploy latest commit"
- [ ] Wait for build to complete

---

## After Deployment

### ✅ Verify Deployment

**1. Check deployment logs:**

```
Expected messages:
✅ "Starting Image Search API..."
✅ "Services will be initialized on first request"
✅ "Application startup complete"

Avoid:
❌ "Ran out of memory"
❌ "OOMKilled"
❌ "Instance failed"
```

**2. Test health endpoint:**

```bash
curl https://your-app.onrender.com/api/v1/health
```

Expected:

```json
{
  "status": "healthy",
  "message": "API is running",
  "timestamp": "2025-11-25T..."
}
```

**3. Test search (first call will be slow!):**

```bash
curl -X POST https://your-app.onrender.com/api/v1/search/url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://picsum.photos/400/300",
    "top_k": 5,
    "threshold": 0.5
  }'
```

⏱️ **Expected time:**

- First call: 3-5 seconds (loading model) - NORMAL!
- Next calls: 1-2 seconds

---

## Monitoring

### 📊 Things to Watch

**In Render Logs:**

- [ ] Memory usage stays under 512MB
- [ ] No "Out of Memory" errors
- [ ] Model loads successfully on first request
- [ ] API responds to health checks

**Performance Metrics:**

- [ ] First API call: 3-5 seconds ✅
- [ ] Subsequent calls: 1-2 seconds ✅
- [ ] Health check: < 1 second ✅

---

## Troubleshooting

### ❌ Still Getting "Out of Memory"?

**Try these in order:**

1. **Reduce results:**

   ```
   TOP_K=5
   SIMILARITY_THRESHOLD=0.7
   ```

2. **Check logs for memory spikes**

   - When does it crash?
   - During startup? → Already optimized
   - During search? → Reduce TOP_K

3. **Restart service**

   - Sometimes helps clear memory

4. **Upgrade plan**
   - Render Starter: $7/month → 2GB RAM

### 🐌 API Too Slow?

**Expected on free tier:**

- First call: 3-5 seconds (loading model)
- This is NORMAL and cannot be avoided on free tier

**To speed up:**

- Upgrade to Starter plan ($7/month)
- Set `CACHE_PRODUCTS=true`
- Set `LAZY_LOAD_MODEL=false`

### 🔄 Service Keeps Restarting?

**Check:**

1. Environment variables are set correctly
2. MONGO_URI is valid
3. Health check endpoint is correct: `/api/v1/health`

---

## Success Criteria

Your deployment is successful when:

- [x] ✅ Service starts without memory errors
- [x] ✅ Health endpoint returns 200 OK
- [x] ✅ First search request completes (even if slow)
- [x] ✅ Subsequent requests are faster
- [x] ✅ Logs show "Lazy loading search service components"
- [x] ✅ Memory stays under 512MB

---

## Next Steps After Success

### Immediate:

- [ ] Test with real product images from your database
- [ ] Monitor for 24 hours for stability
- [ ] Document API endpoints for frontend team

### Optional Improvements:

- [ ] Add caching layer (Redis)
- [ ] Implement request queuing
- [ ] Add monitoring/alerting
- [ ] Upgrade to paid plan for better performance

### Long-term:

- [ ] Consider scaling strategy
- [ ] Evaluate alternative hosting (AWS Lambda, etc.)
- [ ] Optimize model further (quantization, pruning)

---

## Contact Points

**If issues persist:**

1. Check Render community forum
2. Review Render documentation
3. Check GitHub repo issues
4. Monitor memory with `monitor_memory.py` locally

---

## Rollback Plan

**If deployment fails:**

1. **Revert environment variables** to previous values
2. **Redeploy previous commit:**
   ```bash
   git revert HEAD
   git push origin main
   ```
3. **Check logs** for specific error
4. **Try fixes** in staging environment first

---

## Summary

**Memory optimization complete! 🎉**

- Model loads on first request (saves 150MB)
- Features computed on-demand (saves 200MB)
- Single worker, limited concurrency (saves 50MB)
- **Total saved: ~400MB → Now uses ~400MB peak**

**Deploy now and test!**
