from fastapi import FastAPI
from pydantic import BaseModel
from groqchat import get_answer_from_groq
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Custom Chatbot API",
    version="1.0.0",
    description="Backend API for a ChromaDB + Groq-powered chatbot"
)

# Configuration
CHROMA_PATH = "chroma"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load ChromaDB with embeddings
embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
db = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings
)

# Request body model
class QuestionRequest(BaseModel):
    question: str

# Endpoint for asking a question
@app.post("/ask")
async def ask_question(data: QuestionRequest):
    # Search for similar context in ChromaDB
    results = db.similarity_search(data.question, k=3)
    
    if not results:
        return {"answer": "I don't know based on the provided context."}

    # Combine retrieved context
    context = "\n".join([doc.page_content for doc in results])

    # Generate answer from Groq
    answer = get_answer_from_groq(context, data.question)

    return {"answer": answer}

# Run server if executed directly
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
