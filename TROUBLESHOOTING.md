# Troubleshooting: Render Service Down

## 🔍 Current Issue

Your service `fragmentstothought.onrender.com` is showing as **DOWN** in UptimeRobot.

## 🚨 Immediate Diagnostic Steps

### Step 1: Check Render Dashboard

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on your service
3. Check **Logs** tab for errors
4. Check **Events** tab for deployment status

**Look for:**
- ❌ Build failures
- ❌ Runtime errors
- ❌ Environment variable issues
- ❌ Port binding errors

### Step 2: Test Health Endpoint Manually

```bash
# Test health endpoint
curl https://fragmentstothought.onrender.com/health

# Expected response:
# {"status":"healthy","service":"FragmentsToThought RAG API","version":"3.0.0"}
```

**If it times out or errors:**
- Service is crashed or sleeping
- Check Render logs for startup errors

### Step 3: Check Common Issues

#### Issue A: Missing Environment Variables

**Symptoms:**
- Service starts but crashes on first request
- Errors about `QDRANT_URL`, `GROQ_API_KEY`, etc.

**Fix:**
1. Go to Render Dashboard → Your Service → Environment
2. Verify all required variables are set:
   ```
   QDRANT_URL=your-qdrant-url
   QDRANT_API_KEY=your-api-key
   GROQ_API_KEY=your-groq-key
   PORT=10000
   PYTHON_VERSION=3.11.9
   ```

#### Issue B: Import Errors

**Symptoms:**
- Build succeeds but service crashes on startup
- Logs show `ModuleNotFoundError` or `ImportError`

**Fix:**
1. Check `requirements.txt` includes all dependencies
2. Verify Python version matches (`runtime.txt` or `render.yaml`)
3. Check for missing imports in `server.py` or `rag_system.py`

#### Issue C: Port Binding Issues

**Symptoms:**
- Service fails to start
- Logs show "Address already in use" or port errors

**Fix:**
1. Verify `Procfile` uses `$PORT` environment variable
2. Check `render.yaml` has correct port configuration
3. Ensure `uvicorn` binds to `0.0.0.0:$PORT`

#### Issue D: Cold Start Timeout

**Symptoms:**
- Service takes > 60 seconds to start
- Health checks timeout
- Service appears down but eventually responds

**Fix:**
1. ✅ Already implemented: Lazy loading reduces startup time
2. Check if model download is blocking startup
3. Consider pre-warming on startup (paid tier only)

#### Issue E: RAG System Initialization Failure

**Symptoms:**
- Health endpoint works (`/health`)
- `/ask` endpoint fails
- Logs show Qdrant or Groq connection errors

**Fix:**
1. Verify Qdrant URL and API key are correct
2. Test Qdrant connection: `python Tests/testquadrant.py`
3. Verify Groq API key is valid
4. Check network connectivity from Render

---

## 🔧 Quick Fixes

### Fix 1: Restart Service

1. Render Dashboard → Your Service
2. Click **Manual Deploy** → **Clear build cache & deploy**
3. Wait for deployment to complete
4. Check logs for errors

### Fix 2: Verify Health Endpoint

The health endpoint should be **lightweight** and respond quickly:

```python
@app.get("/health")
async def health():
    return {"status": "healthy"}  # No RAG initialization!
```

**Test:**
```bash
time curl https://fragmentstothought.onrender.com/health
# Should respond in < 1 second
```

### Fix 3: Check Build Logs

1. Render Dashboard → Your Service → Logs
2. Look for:
   - ✅ "Build successful"
   - ✅ "Starting server..."
   - ❌ Any red error messages

### Fix 4: Test Locally First

```bash
# Test locally before deploying
python server.py

# In another terminal:
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}
```

---

## 📋 Deployment Checklist

Before deploying, verify:

- [ ] `requirements.txt` is up to date
- [ ] `runtime.txt` specifies Python 3.11.9
- [ ] `Procfile` exists and is correct
- [ ] `render.yaml` is configured (optional but recommended)
- [ ] Environment variables are set in Render dashboard
- [ ] Health endpoint responds quickly (< 1s)
- [ ] Service starts without errors locally

---

## 🐛 Common Error Messages

### Error: "Module not found"

**Solution:**
```bash
# Add missing package to requirements.txt
pip freeze > requirements.txt
# Or add manually:
# missing-package==version
```

### Error: "Connection refused" or "Timeout"

**Solution:**
- Check Qdrant URL is accessible from Render
- Verify API keys are correct
- Check firewall/network settings

### Error: "Port already in use"

**Solution:**
- Ensure using `$PORT` environment variable
- Check `Procfile` is correct
- Verify `render.yaml` port configuration

### Error: "Health check failed"

**Solution:**
- Verify `/health` endpoint exists
- Check endpoint responds in < 30 seconds
- Ensure endpoint doesn't require RAG initialization

---

## 🔍 Debug Mode

Enable debug logging:

1. Add to Render environment variables:
   ```
   DEBUG=true
   LOG_LEVEL=debug
   ```

2. Check logs for detailed error messages

3. Test endpoints:
   ```bash
   curl https://fragmentstothought.onrender.com/health
   curl https://fragmentstothought.onrender.com/
   ```

---

## 📞 Next Steps

1. **Check Render logs** - Most important step
2. **Test health endpoint manually** - Verify it responds
3. **Verify environment variables** - Common cause of failures
4. **Test locally** - Reproduce issue locally if possible
5. **Check build logs** - Look for build-time errors

---

## ✅ Expected Behavior

**Healthy Service:**
- Health endpoint responds in < 1 second
- Returns `{"status": "healthy", ...}`
- UptimeRobot shows "Up" status
- Service stays warm with keep-alive

**If Still Down:**
- Check Render logs for specific error
- Verify all environment variables
- Test endpoints manually
- Consider redeploying with cleared cache

---

## 🚀 Emergency Recovery

If service is completely down:

1. **Redeploy:**
   ```
   Render Dashboard → Manual Deploy → Clear build cache
   ```

2. **Check logs immediately:**
   ```
   Watch logs during startup for errors
   ```

3. **Test health endpoint:**
   ```bash
   curl https://fragmentstothought.onrender.com/health
   ```

4. **If still failing:**
   - Check environment variables
   - Verify dependencies in requirements.txt
   - Test locally to reproduce issue

---

## 📝 Log Analysis

**Good startup logs:**
```
[INFO] Starting FragmentsToThought API...
[INFO] FastAPI application started successfully
[INFO] Health endpoint available at: /health
```

**Bad startup logs:**
```
[ERROR] Failed to initialize RAG system: ...
[ERROR] ModuleNotFoundError: ...
[ERROR] Connection refused: ...
```

Look for `[ERROR]` lines in Render logs to identify the issue.
