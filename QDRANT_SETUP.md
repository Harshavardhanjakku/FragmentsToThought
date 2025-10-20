# 🚀 Qdrant Cloud Setup Guide

This guide will help you migrate from ChromaDB to Qdrant Cloud for **lightning-fast Vercel deployments**.

## Why Qdrant Cloud?

- ✅ **No model downloads** - Uses API-based embeddings
- ✅ **Serverless-friendly** - No heavy dependencies
- ✅ **1GB free forever** - No credit card required
- ✅ **Fast deployments** - Deploys in seconds, not minutes

## Step 1: Create Qdrant Cloud Account

1. Go to [Qdrant Cloud](https://cloud.qdrant.io/)
2. Click "Start Free" (no credit card needed)
3. Create a new cluster
4. Copy your credentials:
   - **URL**: `https://your-cluster-name.qdrant.tech`
   - **API Key**: `your-api-key-here`

## Step 2: Set Environment Variables

Add to your `.env` file:

```env
# Existing
GROQ_API_KEY=your_groq_api_key_here

# New Qdrant credentials
QDRANT_URL=https://your-cluster-name.qdrant.tech
QDRANT_API_KEY=your_qdrant_api_key_here

# Optional: HuggingFace token for better embeddings
HF_TOKEN=your_hf_token_here
```

## Step 3: Migrate Your Data

Run the migration script to move your ChromaDB data to Qdrant:

```bash
python migrate_to_qdrant.py
```

This will:
- Connect to your Qdrant Cloud cluster
- Create a collection called `fragments_to_thought`
- Migrate all your documents and embeddings
- Show progress as it uploads

## Step 4: Test Locally

Test the new Qdrant-powered chatbot:

```bash
python groqchat.py
```

## Step 5: Deploy to Vercel

Your Vercel deployment will now be **much faster** because:

- ❌ No more HuggingFace model downloads (400MB+)
- ❌ No more ChromaDB initialization
- ❌ No more heavy dependencies (torch, transformers, etc.)
- ✅ Just lightweight API calls to Qdrant Cloud

### Vercel Environment Variables

Add these to your Vercel project settings:

```
GROQ_API_KEY=your_groq_api_key
QDRANT_URL=https://your-cluster-name.qdrant.tech
QDRANT_API_KEY=your_qdrant_api_key
HF_TOKEN=your_hf_token (optional)
```

## Step 6: Test Your API

Your API endpoint is now at: `https://your-app.vercel.app/api/ask`

Test with:

```bash
curl -X POST "https://your-app.vercel.app/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me about Harsha"}'
```

## Performance Comparison

| Metric | ChromaDB Version | Qdrant Cloud Version |
|--------|------------------|---------------------|
| Cold Start | 30-60 seconds | 2-5 seconds |
| Bundle Size | 400MB+ | <10MB |
| Dependencies | 147 packages | 6 packages |
| Memory Usage | 1GB+ | <100MB |

## Troubleshooting

### Migration Issues
- Make sure your `.env` has correct Qdrant credentials
- Check that your ChromaDB data exists in the `chroma/` folder
- Verify your Qdrant cluster is running

### Deployment Issues
- Ensure all environment variables are set in Vercel
- Check Vercel function logs for errors
- Verify your Qdrant collection exists

### API Issues
- Test locally first with `python groqchat.py`
- Check that your Groq API key is valid
- Verify Qdrant Cloud cluster is accessible

## Next Steps

1. **Monitor Usage**: Check your Qdrant Cloud dashboard for usage stats
2. **Scale Up**: Upgrade to paid plan if you need more than 1GB
3. **Add More Data**: Use the migration script again to add new documents
4. **Optimize**: Fine-tune your chunking strategy for better results

---

🎉 **Congratulations!** Your RAG chatbot is now optimized for serverless deployment and will deploy in seconds instead of timing out!
