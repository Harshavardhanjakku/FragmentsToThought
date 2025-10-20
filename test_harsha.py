#!/usr/bin/env python3
"""
Test chatbot with better timeout handling
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
import requests
import hashlib
from groq import Groq

load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "fragments_to_thought"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"

# Initialize clients
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)
groq_client = Groq(api_key=GROQ_API_KEY)

def get_simple_embedding(text: str) -> list:
    """Create a simple hash-based embedding"""
    hash_obj = hashlib.md5(text.encode())
    hash_bytes = hash_obj.digest()
    embedding = []
    for i in range(384):
        embedding.append((hash_bytes[i % len(hash_bytes)] - 128) / 128.0)
    return embedding

def search_qdrant_simple(query: str, k: int = 3) -> list:
    """Search Qdrant with simple embeddings"""
    try:
        print(f"Searching for: {query}")
        query_embedding = get_simple_embedding(query)
        
        # Search with longer timeout
        search_results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=k,
            timeout=60
        )
        
        print(f"Found {len(search_results.points)} results")
        return search_results.points
        
    except Exception as e:
        print(f"Search error: {e}")
        return []

def get_answer_from_groq(context: str, question: str) -> str:
    """Generate answer using Groq LLM"""
    prompt = f"""
You are a helpful assistant. Answer the question based on the provided context.

CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
- If the context contains relevant information, provide a detailed answer.
- If the context doesn't have enough information, say "I don't have enough information about this topic."
"""
    
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You're a helpful assistant that answers based on context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=512
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {e}"

def test_questions():
    """Test various questions about Harsha"""
    questions = [
        "Tell me about Jakku Harshavardhan",
        "Who is Harsha?",
        "What is Harsha's education?",
        "What projects has Harsha worked on?",
        "What are Harsha's technical skills?",
        "Tell me about Harsha's patents",
        "What is Harsha's CGPA?",
        "Where does Harsha study?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        print("-" * 60)
        
        # Search Qdrant
        results = search_qdrant_simple(question, k=3)
        
        if not results:
            print("Answer: I don't have enough information about this topic.")
            continue
        
        # Build context
        context_parts = []
        for result in results:
            content = result.payload.get('content', '')
            if content:
                context_parts.append(content)
        
        if not context_parts:
            print("Answer: I don't have enough information about this topic.")
            continue
        
        context = "\n\n".join(context_parts)
        
        # Generate answer
        print("Generating answer...")
        answer = get_answer_from_groq(context, question)
        print(f"Answer: {answer}")
        print("-" * 60)

if __name__ == "__main__":
    test_questions()
