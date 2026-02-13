#!/usr/bin/env python3
"""
🔥 Production-Grade LOCAL RAG System (Chroma + Groq)
- Local ChromaDB
- Real embeddings
- Clean retrieval
- Resume-safe (Jakku Harshavardhan only)
"""

import os
import warnings
from typing import List

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq

# Load environment variables
load_dotenv()

# Suppress specific non-critical huggingface FutureWarning
warnings.filterwarnings(
    "ignore",
    message="`resume_download` is deprecated and will be removed in version 1.0.0",
    category=FutureWarning,
)


class LocalRAGSystem:
    def __init__(self):
        # ENV
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")

        self.CHROMA_PATH = "chroma"
        self.MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

        # Embeddings (MUST match create_database.py)
        self.embedder = HuggingFaceEmbeddings(
            model_name=self.MODEL_NAME
        )

        # Load Local Chroma DB
        self.db = Chroma(
            persist_directory=self.CHROMA_PATH,
            embedding_function=self.embedder
        )

        # Groq LLM
        self.llm = Groq(api_key=self.GROQ_API_KEY)

    # ─────────────────────────────────────────────
    # RETRIEVAL
    # ─────────────────────────────────────────────

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        """Retrieve top-k contexts from local Chroma for a given query."""
        results = self.db.similarity_search(query, k=k)

        contexts: List[str] = []
        for doc in results:
            if doc.page_content:
                contexts.append(doc.page_content)

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
rag = LocalRAGSystem()


# CLI Testing
if __name__ == "__main__":
    print("🔥 LOCAL RAG SYSTEM READY (Chroma + Groq)")
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
        print("\nExiting LOCAL RAG system.")
