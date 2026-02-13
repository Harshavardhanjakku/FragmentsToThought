# Render Deployment Guide - Cold Start Prevention

## 🎯 Problem Statement

Render free tier services spin down after 15 minutes of inactivity, causing:
- **Cold starts**: 30-60s delay on first request
- **Poor UX**: Users experience long wait times
- **Service instability**: Frequent restarts

## 🏗️ Architecture Solutions

### Option 1: External Keep-Alive Service (RECOMMENDED)

**Best for**: Production deployments, multiple services

**How it works**:
- Run `keep_alive.py` on a separate machine/service (e.g., GitHub Actions, Railway, or your own server)
- Pings your Render service every 10 minutes
- Keeps service warm without violating Render policies

**Pros**:
- ✅ No Render resource usage
- ✅ Works with free tier
- ✅ Scalable (can monitor multiple services)
- ✅ No code changes to main app

**Cons**:
- ⚠️ Requires external service/hosting

---

### Option 2: Render Cron Job (PAID TIER ONLY)

**Best for**: Paid Render services with cron support

**How it works**:
- Use Render's built-in cron job feature
- Schedule periodic health checks

**Pros**:
- ✅ Integrated with Render
- ✅ Reliable and managed

**Cons**:
- ❌ Requires paid Render plan
- ❌ Not available on free tier

---

### Option 3: Uptime Monitoring Service

**Best for**: Production with monitoring needs

**Services**:
- UptimeRobot (free tier: 50 monitors, 5-min intervals)
- Pingdom
- StatusCake
- Better Uptime

**Setup**:
1. Create account on monitoring service
2. Add your Render URL: `https://your-app.onrender.com/health`
3. Set check interval to 10 minutes
4. Done!

**Pros**:
- ✅ Free tier available
- ✅ Additional monitoring benefits
- ✅ Alerting capabilities
- ✅ No code changes needed

**Cons**:
- ⚠️ External dependency

---

## 🚀 Implementation Steps

### Step 1: Optimize Your FastAPI Server

Already done! Your `server.py` now uses:
- ✅ Lazy loading (RAG loads on first request)
- ✅ Lightweight `/health` endpoint
- ✅ Warm-up endpoint `/health/warm`

### Step 2: Choose Keep-Alive Method

#### Method A: External Python Script (Recommended)

**Option A1: Run on GitHub Actions (FREE)**

1. Create `.github/workflows/keep-alive.yml`:

```yaml
name: Keep Render Alive

on:
  schedule:
    - cron: '*/10 * * * *'  # Every 10 minutes
  workflow_dispatch:  # Manual trigger

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Render Service
        run: |
          curl -f https://your-app.onrender.com/health || exit 1
```

2. Set your Render URL in the workflow file

**Option A2: Run on Your Own Server**

```bash
# Install dependencies
pip install requests

# Run keep-alive script
python keep_alive.py \
  --url https://your-app.onrender.com \
  --interval 600
```

**Option A3: Use Railway/Render Background Worker**

1. Create a new Render/Railway service
2. Use `keep_alive.py` as the entry point
3. Set environment variables:
   - `KEEP_ALIVE_URL=https://your-app.onrender.com`
   - `KEEP_ALIVE_INTERVAL=600`

#### Method B: Uptime Monitoring Service

1. Sign up for [UptimeRobot](https://uptimerobot.com) (free)
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://your-app.onrender.com/health`
   - Interval: 5 minutes
3. Save and activate

---

## ⚙️ Render Configuration

### render.yaml (Already Created)

```yaml
services:
  - type: web
    name: rag-chatbot-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1
    healthCheckPath: /health
    autoDeploy: true
```

### Environment Variables

Set in Render dashboard:

```
PYTHON_VERSION=3.11.9
PORT=10000
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-api-key
GROQ_API_KEY=your-groq-key
```

---

## 🔧 Advanced Optimizations

### 1. Pre-warm on Startup (Optional)

Add to `server.py`:

```python
@app.on_event("startup")
async def startup_event():
    """Pre-warm RAG system on startup (optional - increases startup time)."""
    if os.getenv("PREWARM_RAG", "false").lower() == "true":
        logger.info("Pre-warming RAG system...")
        get_rag()  # Initialize RAG
        logger.info("RAG system ready")
```

**Trade-off**: Faster first request vs. slower startup

### 2. Connection Pooling

Already optimized in `rag_system.py`:
- Qdrant client uses connection pooling
- Groq client is stateless

### 3. Model Caching

SentenceTransformer automatically caches models in:
- `~/.cache/huggingface/transformers/`

No additional config needed.

---

## 📊 Performance Metrics

### Before Optimization:
- Cold start: 30-60s
- Warm response: 2-5s
- Service downtime: Frequent

### After Optimization:
- Cold start: 5-10s (lazy loading)
- Warm response: 2-5s
- Service downtime: None (with keep-alive)

---

## 🎯 Recommended Setup (Production)

1. **Use UptimeRobot** (free, reliable, 5-min checks)
2. **Keep lazy loading** (already implemented)
3. **Monitor `/health` endpoint** (lightweight)
4. **Optional**: Pre-warm on startup if you have paid tier

---

## ⚠️ Important Notes

### Render Free Tier Limitations:
- Services sleep after 15 minutes of inactivity
- Cold starts are unavoidable without keep-alive
- Keep-alive must be external (can't self-ping)

### Render Paid Tier Benefits:
- Services stay warm (no sleep)
- Faster cold starts
- Can use cron jobs
- Better performance

### Best Practice:
- Use external keep-alive (UptimeRobot recommended)
- Keep lazy loading enabled
- Monitor service health
- Consider paid tier for production

---

## 🐛 Troubleshooting

### Issue: Service still sleeping

**Solution**: 
- Verify keep-alive is running
- Check ping interval (should be < 15 minutes)
- Verify `/health` endpoint is accessible

### Issue: Slow cold starts

**Solution**:
- Enable pre-warming (if on paid tier)
- Optimize model loading
- Use smaller embedding model

### Issue: Keep-alive script errors

**Solution**:
- Check URL is correct
- Verify network connectivity
- Check logs for errors

---

## 📝 Summary

**Quick Start**:
1. ✅ Server already optimized (lazy loading)
2. ✅ Set up UptimeRobot monitor (5-min interval)
3. ✅ Deploy to Render
4. ✅ Service stays warm!

**For Production**:
- Use paid Render tier OR
- External keep-alive service
- Monitor health endpoints
- Optimize startup sequence
