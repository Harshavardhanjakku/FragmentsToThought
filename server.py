from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title="FragmentsToThought API - RAG",
    version="3.0.0",
    description="Grounded RAG chatbot using Qdrant + Groq"
)

# -----------------------------
# LAZY LOADING: RAG System
# -----------------------------
# Load RAG system only when first request arrives (reduces cold start time)
_rag_instance = None

def get_rag():
    """Lazy-load RAG system singleton."""
    global _rag_instance
    if _rag_instance is None:
        # Import here to avoid eager loading on startup
        from rag_system import RAGSystem
        _rag_instance = RAGSystem()
    return _rag_instance

# -----------------------------
# CORS CONFIG (VERY IMPORTANT)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # later you can restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],        # allows POST, OPTIONS, etc.
    allow_headers=["*"],
)

# -----------------------------
# Request Model
# -----------------------------
class QuestionRequest(BaseModel):
    question: str

# -----------------------------
# ASK ENDPOINT
# -----------------------------
@app.post("/ask")
async def ask_question(data: QuestionRequest):
    try:
        rag = get_rag()  # Lazy load on first request
        answer = rag.ask(data.question)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"[ERROR] {str(e)}"}

# -----------------------------
# OPTIONS (Preflight) ENDPOINT
# 🔴 THIS FIXES 405 + CORS ERROR
# -----------------------------
@app.options("/ask")
async def options_ask():
    return {}

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/health")
async def health():
    """Health check endpoint - lightweight, no RAG initialization."""
    return {
        "status": "healthy",
        "service": "FragmentsToThought RAG API"
    }

@app.get("/health/warm")
async def health_warm():
    """Warm-up endpoint - initializes RAG system to reduce cold start latency."""
    try:
        rag = get_rag()  # Trigger lazy loading
        return {
            "status": "healthy",
            "rag_initialized": True,
            "service": "FragmentsToThought RAG API"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "rag_initialized": False,
            "error": str(e)
        }

# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
async def root():
    return {
        "message": "FragmentsToThought RAG API",
        "endpoints": {
            "ask": "/ask",
            "health": "/health",
            "docs": "/docs"
        }
    }

# -----------------------------
# LOCAL RUN
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
