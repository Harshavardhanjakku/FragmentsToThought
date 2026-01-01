#!/usr/bin/env python3
"""
🔥 Production-Grade RAG System (Qdrant + Groq)
- REAL embeddings
- Correct Qdrant payload handling
- Render-safe
- No fake vectors
"""

import os
from typing import List
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from groq import Groq
from sentence_transformers import SentenceTransformer

load_dotenv()


class RAGSystem:
    def __init__(self):
        # ENV
        self.QDRANT_URL = os.getenv("QDRANT_URL")
        self.QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")

        self.COLLECTION_NAME = "fragments_to_thought"

        # Clients
        self.qdrant = QdrantClient(
            url=self.QDRANT_URL,
            api_key=self.QDRANT_API_KEY,
            timeout=60
        )

        self.llm = Groq(api_key=self.GROQ_API_KEY)

        # MUST match migration model
        self.embedder = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    # ─────────────────────────────────────────────
    # SEARCH
    # ─────────────────────────────────────────────

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        vector = self.embedder.encode(query).tolist()

        results = self.qdrant.query_points(
            collection_name=self.COLLECTION_NAME,
            query=vector,
            limit=k,
            with_payload=True
        )

        contexts = []
        for point in results.points:
            payload = point.payload or {}
            content = payload.get("content")
            if content:
                contexts.append(content)

        return contexts

    # ─────────────────────────────────────────────
    # GENERATION
    # ─────────────────────────────────────────────

    def generate(self, query: str, contexts: List[str]) -> str:
        if not contexts:
            return "I don't have sufficient information in my knowledge base."

        context_text = "\n\n".join(contexts)

        prompt = f"""
You are an AI assistant.
Answer ONLY using the context below.

CONTEXT:
{context_text}

QUESTION:
{query}

IMPORTANT RULES:
- Your knowledge domain is ONLY Jakku Harshavardhan.
- If the user greets (hi, hello, hey), respond with a friendly greeting.
- If the user asks who you are, say: "I am Harsha's helpful bot."
- If the question is about Jakku Harshavardhan (or Harsha / Jakku):
    - Answer ONLY using the provided context.
- If the question is NOT about Jakku Harshavardhan, say: "I don't know."
- If the answer is not clearly present in the context, say: "I don't know."
- Do NOT hallucinate or add external knowledge.
If the answer is not in context, say you don't know.
"""

        response = self.llm.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600
        )

        return response.choices[0].message.content.strip()

    # ─────────────────────────────────────────────
    # MAIN ENTRY
    # ─────────────────────────────────────────────

    def ask(self, query: str) -> str:
        print(f"🔍 Query: {query}")

        contexts = self.retrieve(query)

        print(f"📚 Retrieved {len(contexts)} chunks")

        return self.generate(query, contexts)


# Global instance
rag = RAGSystem()


# CLI testing
if __name__ == "__main__":
    print("🔥 RAG SYSTEM READY (Qdrant + Groq)")
    print("Type 'exit' to quit\n")

    while True:
        q = input("Ask: ").strip()
        if q.lower() in {"exit", "quit"}:
            break

        print("\n" + "=" * 60)
        print(rag.ask(q))
        print("=" * 60 + "\n")
