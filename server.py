from fastapi import FastAPI
from pydantic import BaseModel
from rag_system import rag_system
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="FragmentsToThought API - Advanced RAG",
    version="3.0.0",
    description="State-of-the-art RAG chatbot powered by Advanced Query Processing + Qdrant Cloud + Groq"
)

# Request body model
class QuestionRequest(BaseModel):
    question: str

# Endpoint for asking a question
@app.post("/ask")
async def ask_question(data: QuestionRequest):
    try:
        # Use advanced RAG system
        answer = rag_system.ask_question(data.question)
        return {"answer": answer}
        
    except Exception as e:
        return {"answer": f"[ERROR] Failed to process question: {str(e)}"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Advanced RAG API", "version": "3.0.0"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "FragmentsToThought API - Advanced RAG System",
        "version": "3.0.0",
        "endpoints": {
            "ask": "/ask",
            "health": "/health",
            "docs": "/docs"
        }
    }

# Run server if executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)