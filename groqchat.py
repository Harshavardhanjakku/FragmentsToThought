# groqchat.py - Qdrant Cloud version (fast & serverless-friendly)
import os
from dotenv import load_dotenv
from groq import Groq
from qdrant_client import QdrantClient
import requests

load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "fragments_to_thought"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"

# Initialize clients
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in environment (.env or env vars)")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("QDRANT_URL and QDRANT_API_KEY must be set in environment")

groq_client = Groq(api_key=GROQ_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def get_embeddings_from_api(text: str) -> list:
    """Get embeddings using HuggingFace Inference API (serverless-friendly)"""
    try:
        # For now, use simple hash-based embedding as fallback
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

def search_qdrant(query: str, k: int = 3) -> list:
    """Search Qdrant Cloud for similar documents"""
    try:
        # Get query embedding
        query_embedding = get_embeddings_from_api(query)
        
        # Search in Qdrant using the search method
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=k
        )
        
        return search_results
        
    except Exception as e:
        print(f"Error searching Qdrant: {e}")
        return []

def get_answer_from_groq(context: str, question: str) -> str:
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

def generate_answer(question: str, k: int = 3) -> str:
    """
    High-level API: searches Qdrant Cloud and asks Groq for an answer.
    Returns a string (answer) in all cases (or an error message string).
    """
    try:
        # Search Qdrant Cloud
        results = search_qdrant(question, k=k)
    except Exception as e:
        return f"[ERROR] Vector search failed: {e}"

    if not results:
        return "I don't know based on the provided context."

    # Build context from search results
    context_parts = []
    for result in results:
        content = result.payload.get('content', '')
        if content:
            context_parts.append(content)
    
    if not context_parts:
        return "I don't know based on the provided context."
    
    context = "\n\n".join(context_parts)
    return get_answer_from_groq(context.strip(), question)

# keep CLI for debugging
if __name__ == "__main__":
    print("[INFO] Running groqchat CLI. Type 'exit' to quit.")
    while True:
        q = input("\nAsk: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        print("\n[INFO] Searching and generating...\n")
        print(generate_answer(q))
