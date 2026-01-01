from fastapi import FastAPI
from pydantic import BaseModel
from rag_system import rag
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="FragmentsToThought API - RAG",
    version="3.0.0",
    description="Grounded RAG chatbot using Qdrant + Groq"
)

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(data: QuestionRequest):
    try:
        answer = rag.ask(data.question)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"[ERROR] {str(e)}"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {
        "message": "FragmentsToThought RAG API",
        "endpoints": ["/ask", "/health", "/docs"]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
