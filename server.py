from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_system import rag
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
    return {"status": "healthy"}

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
