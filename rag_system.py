#!/usr/bin/env python3
"""
🔥 Production-Grade RAG System (Qdrant + Groq)
- REAL embeddings
- Correct Qdrant payload handling
- Render-safe
- No fake vectors
"""

import os
import warnings
from typing import List

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from groq import Groq
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Suppress specific non-critical huggingface FutureWarning
warnings.filterwarnings(
    "ignore",
    message="`resume_download` is deprecated and will be removed in version 1.0.0",
    category=FutureWarning,
)


class RAGSystem:
    def __init__(self):
        # ENV
        self.QDRANT_URL = os.getenv("QDRANT_URL")
        self.QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")

        self.COLLECTION_NAME = "fragments_to_thought"

        # Clients (lazy-loaded for faster startup)
        self._qdrant = None
        self._llm = None
        self._embedder = None

    @property
    def qdrant(self):
        """Lazy-load Qdrant client."""
        if self._qdrant is None:
            self._qdrant = QdrantClient(
                url=self.QDRANT_URL,
                api_key=self.QDRANT_API_KEY,
                timeout=60
            )
        return self._qdrant

    @property
    def llm(self):
        """Lazy-load Groq LLM client."""
        if self._llm is None:
            self._llm = Groq(api_key=self.GROQ_API_KEY)
        return self._llm

    @property
    def embedder(self):
        """Lazy-load SentenceTransformer (heaviest initialization)."""
        if self._embedder is None:
            # MUST match migration model
            self._embedder = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        return self._embedder

    # ─────────────────────────────────────────────
    # SEARCH
    # ─────────────────────────────────────────────

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        """Retrieve top-k contexts from Qdrant for a given query."""
        vector = self.embedder.encode(query).tolist()

        results = self.qdrant.query_points(
            collection_name=self.COLLECTION_NAME,
            query=vector,
            limit=k,
            with_payload=True,
            score_threshold=0.3,  # similarity guard (cosine similarity: 0.3-0.9 typical range)
        )

        contexts: List[str] = []
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
You are Harsha's helpful bot. You answer questions about Jakku Harshavardhan using ONLY the CONTEXT provided below.

STRICT RULES:
1. Answer ONLY using information from CONTEXT. Do not add information not in CONTEXT.
2. If the question is clearly about Jakku Harshavardhan (or variations: Harsha, Jakku, Harshavardhan), answer using CONTEXT.
3. If the question is NOT about Jakku Harshavardhan, answer exactly: "I don't know."
4. If CONTEXT contains relevant information, use it to answer. Do not say "I don't know" if CONTEXT has the answer.
5. Keep answers concise and factual.
6. If the user only greets (hi, hello, hey) without asking a question, respond with a short friendly greeting mentioning you are Harsha's helpful bot.

CONTEXT:
{context_text}

QUESTION:
{query}

Answer based on CONTEXT:
"""

        response = self.llm.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=600
        )

        return response.choices[0].message.content.strip()

    # ─────────────────────────────────────────────
    # MAIN ENTRY
    # ─────────────────────────────────────────────

    def ask(self, query: str) -> str:
        """Main entrypoint for answering a user query."""
        query = (query or "").strip()
        if not query:
            return "Please enter a question so I can help you."

        print(f"[RAG] query={query!r}")

        contexts = self.retrieve(query)

        print(f"[RAG] retrieved_k={len(contexts)}")

        return self.generate(query, contexts)


# Global instance
rag = RAGSystem()


# CLI testing
if __name__ == "__main__":
    print("🔥 RAG SYSTEM READY (Qdrant + Groq)")
    print("Type 'exit' to quit\n")

    try:
        while True:
            q = input("Ask: ").strip()
            if q.lower() in {"exit", "quit"}:
                break
            if not q:
                print("Please enter a question (or type 'exit' to quit).")
                continue

            print("\n" + "=" * 60)
            print(rag.ask(q))
            print("=" * 60 + "\n")
    except KeyboardInterrupt:
        print("\nExiting RAG system.")
