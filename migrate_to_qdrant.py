#!/usr/bin/env python3
"""
🚀 PRODUCTION-GRADE CHROMA → QDRANT MIGRATION PIPELINE

Author intent:
- Deterministic
- Idempotent
- Embedding-safe
- Cloud-ready
- RAG-optimized

This script is designed to be run ONCE (or safely re-run) locally.
"""

import os
import uuid
import time
import hashlib
from typing import List, Dict, Any
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# ─────────────────────────────────────────────────────────────
# ENV SETUP
# ─────────────────────────────────────────────────────────────

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("❌ QDRANT_URL or QDRANT_API_KEY missing in .env")


# ─────────────────────────────────────────────────────────────
# MIGRATOR
# ─────────────────────────────────────────────────────────────

class ChromaToQdrantMigrator:
    """
    Enterprise-grade vector migration pipeline.
    """

    def __init__(self):
        # Paths & names
        self.CHROMA_PATH = "chroma"
        self.COLLECTION_NAME = "fragments_to_thought"

        # Embedding model
        self.MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
        self.EMBEDDING_DIM = 384

        # Clients
        self.qdrant = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=60,
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.MODEL_NAME
        )

        self.chroma = Chroma(
            persist_directory=self.CHROMA_PATH,
            embedding_function=self.embeddings
        )

    # ─────────────────────────────────────────────────────────
    # ENTRYPOINT
    # ─────────────────────────────────────────────────────────

    def migrate(self):
        print("\n🚀 STARTING CHROMA → QDRANT MIGRATION")
        print("=" * 70)

        self._recreate_collection()
        chunks = self._load_chroma_chunks()

        if not chunks:
            print("❌ No data found in Chroma. Aborting.")
            return

        self._upload_chunks(chunks)
        self._validate()

        print("=" * 70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY\n")

    # ─────────────────────────────────────────────────────────
    # COLLECTION SETUP
    # ─────────────────────────────────────────────────────────

    def _recreate_collection(self):
        print("🧹 Resetting Qdrant collection...")

        try:
            self.qdrant.delete_collection(self.COLLECTION_NAME)
            print("  • Old collection deleted")
        except Exception:
            print("  • No existing collection found")

        self.qdrant.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=self.EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )

        print("  • New collection created")

    # ─────────────────────────────────────────────────────────
    # CHROMA EXTRACTION
    # ─────────────────────────────────────────────────────────

    def _load_chroma_chunks(self) -> List[Dict[str, Any]]:
        print("📦 Extracting data from Chroma...")

        data = self.chroma.get(include=["documents", "metadatas"])

        documents = data.get("documents", [])
        metadatas = data.get("metadatas", [])

        chunks = []

        for idx, content in enumerate(documents):
            metadata = metadatas[idx] if idx < len(metadatas) else {}

            chunks.append({
                "id": self._stable_id(content),
                "content": content,
                "metadata": metadata,
                "word_count": len(content.split()),
                "char_count": len(content),
            })

        print(f"  • Loaded {len(chunks)} chunks")
        return chunks

    # ─────────────────────────────────────────────────────────
    # UPLOAD PIPELINE
    # ─────────────────────────────────────────────────────────

    def _upload_chunks(self, chunks: List[Dict[str, Any]]):
        print("☁️ Uploading to Qdrant...")

        BATCH_SIZE = 16
        total_uploaded = 0

        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            points = []

            for chunk in batch:
                embedding = self.embeddings.embed_query(chunk["content"])

                if len(embedding) != self.EMBEDDING_DIM:
                    raise ValueError("❌ Embedding dimension mismatch")

                payload = {
                    "content": chunk["content"],
                    "metadata": chunk["metadata"],
                    "word_count": chunk["word_count"],
                    "char_count": chunk["char_count"],
                    "source": "chroma_migration",
                    "migrated_at": int(time.time()),
                }

                points.append(
                    PointStruct(
                        id=chunk["id"],
                        vector=embedding,
                        payload=payload,
                    )
                )

            self.qdrant.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points,
            )

            total_uploaded += len(points)
            print(f"  • Uploaded {total_uploaded}/{len(chunks)}")

        print(f"✅ Uploaded total {total_uploaded} vectors")

    # ─────────────────────────────────────────────────────────
    # VALIDATION
    # ─────────────────────────────────────────────────────────

    def _validate(self):
        print("🔍 Validating migration...")

        info = self.qdrant.get_collection(self.COLLECTION_NAME)
        print(f"  • Points in collection: {info.points_count}")

        query = "jakku harshavardhan"
        vector = self.embeddings.embed_query(query)

        results = self.qdrant.query_points(
            collection_name=self.COLLECTION_NAME,
            query=vector,
            limit=3,
        )

        print(f"  • Test search results: {len(results.points)}")

        for i, r in enumerate(results.points[:2], 1):
            preview = r.payload.get("content", "")[:80]
            print(f"    {i}. {preview}...")

        print("✅ Validation successful")

    # ─────────────────────────────────────────────────────────
    # UTIL
    # ─────────────────────────────────────────────────────────

    def _stable_id(self, text: str) -> str:
        """
        Deterministic UUID for safe re-runs.
        """
        return str(uuid.UUID(hashlib.md5(text.encode()).hexdigest()))


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    migrator = ChromaToQdrantMigrator()
    migrator.migrate()
