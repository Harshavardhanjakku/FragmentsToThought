from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import uvicorn
import os
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="FragmentsToThought API",
    version="2.0.0",
    description="Fast RAG chatbot powered by Qdrant Cloud + Groq"
)

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "fragments_to_thought"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"

# Initialize clients
if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("QDRANT_URL and QDRANT_API_KEY must be set")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY must be set")

qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# Request body model
class QuestionRequest(BaseModel):
    question: str

def get_embeddings_from_api(text: str) -> list:
    """Get embeddings using HuggingFace Inference API (serverless-friendly)"""
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2",
            headers={"Authorization": f"Bearer {os.getenv('HF_TOKEN', '')}"},
            json={"inputs": text}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            # Fallback: simple hash-based embedding
            import hashlib
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            embedding = []
            for i in range(384):
                embedding.append((hash_bytes[i % len(hash_bytes)] - 128) / 128.0)
            return embedding
            
    except Exception as e:
        # Fallback embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = []
        for i in range(384):
            embedding.append((hash_bytes[i % len(hash_bytes)] - 128) / 128.0)
        return embedding

def get_answer_from_groq(context: str, question: str) -> str:
    """Generate answer using Groq LLM"""
    prompt = f"""
You are a highly knowledgeable assistant trained to answer based **strictly** on the given context.

CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
- If the context is relevant, give a complete, clear answer.
- If the context is vague or doesn't have the answer, respond only with: "I don't know based on the provided context."
"""
    
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You're an AI assistant that answers strictly based on the context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=512
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR] Failed to generate response from Groq: {e}"

# Endpoint for asking a question
@app.post("/ask")
async def ask_question(data: QuestionRequest):
    try:
        # Get query embedding
        query_embedding = get_embeddings_from_api(data.question)
        
        # Search in Qdrant Cloud
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=3
        )
        
        if not search_results:
            return {"answer": "I don't know based on the provided context."}

        # Combine retrieved context
        context_parts = []
        for result in search_results:
            content = result.payload.get('content', '')
            if content:
                context_parts.append(content)
        
        if not context_parts:
            return {"answer": "I don't know based on the provided context."}
            
        context = "\n\n".join(context_parts)

        # Generate answer from Groq
        answer = get_answer_from_groq(context, data.question)

        return {"answer": answer}
        
    except Exception as e:
        return {"answer": f"[ERROR] Failed to process question: {str(e)}"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "FragmentsToThought API"}

# Run server if executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)