from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title="FragmentsToThought API - RAG",
    version="3.0.0",
    description="Grounded RAG chatbot using Qdrant + Groq"
)

# Log startup
logger.info("Starting FragmentsToThought API...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")

# -----------------------------
# LAZY LOADING: RAG System
# -----------------------------
# Load RAG system only when first request arrives (reduces cold start time)
_rag_instance = None

def get_rag():
    """Lazy-load RAG system singleton."""
    global _rag_instance
    if _rag_instance is None:
        try:
            logger.info("Initializing RAG system...")
            # Import here to avoid eager loading on startup
            from rag_system import RAGSystem
            _rag_instance = RAGSystem()
            logger.info("RAG system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=503,
                detail=f"RAG system initialization failed: {str(e)}"
            )
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
        logger.info(f"Received question: {data.question[:50]}...")
        rag = get_rag()  # Lazy load on first request
        answer = rag.ask(data.question)
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"answer": f"[ERROR] {str(e)}"}
        )

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
@app.api_route("/health", methods=["GET", "HEAD", "POST"])
async def health():
    """
    Health check endpoint - lightweight, no RAG initialization.
    Must respond quickly (< 1s) for Render health checks.
    """
    try:
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "FragmentsToThought RAG API",
                "version": "3.0.0"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

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
# STARTUP EVENT
# -----------------------------
@app.on_event("startup")
async def startup_event():
    """Log startup completion."""
    logger.info("FastAPI application started successfully")
    logger.info("Health endpoint available at: /health")
    logger.info("API docs available at: /docs")

# -----------------------------
# EXCEPTION HANDLER
# -----------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An error occurred"
        }
    )

# -----------------------------
# LOCAL RUN
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}...")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
