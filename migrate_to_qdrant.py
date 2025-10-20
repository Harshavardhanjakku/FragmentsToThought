#!/usr/bin/env python3
"""
Migration script to move from ChromaDB to Qdrant Cloud
Run this once to migrate your existing ChromaDB data to Qdrant Cloud
"""

import os
import json
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import uuid

load_dotenv()

# Configuration
CHROMA_PATH = "chroma"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "fragments_to_thought"

def migrate_to_qdrant():
    """Migrate ChromaDB data to Qdrant Cloud"""
    
    if not QDRANT_URL or not QDRANT_API_KEY:
        print("❌ Please set QDRANT_URL and QDRANT_API_KEY in your .env file")
        return
    
    print("🔄 Starting migration from ChromaDB to Qdrant Cloud...")
    
    # Initialize Qdrant client
    print("🔗 Connecting to Qdrant Cloud...")
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
    
    # Create collection if it doesn't exist
    print(f"📦 Creating collection '{COLLECTION_NAME}'...")
    try:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,  # all-MiniLM-L6-v2 embedding size
                distance=Distance.COSINE
            )
        )
        print("✅ Collection created successfully")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("ℹ️ Collection already exists, continuing...")
        else:
            print(f"❌ Error creating collection: {e}")
            return
    
    # Load existing ChromaDB
    print("📂 Loading existing ChromaDB...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        chroma_db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings
        )
        
        # Get all documents from ChromaDB
        print("🔍 Retrieving all documents from ChromaDB...")
        all_docs = chroma_db.get()
        
        if not all_docs or not all_docs.get('documents'):
            print("❌ No documents found in ChromaDB")
            return
            
        documents = all_docs['documents']
        embeddings_list = all_docs['embeddings']
        metadatas = all_docs['metadatas']
        ids = all_docs['ids']
        
        print(f"📄 Found {len(documents)} documents to migrate")
        
        # Prepare points for Qdrant
        points = []
        for i, (doc, embedding, metadata, doc_id) in enumerate(zip(documents, embeddings_list, metadatas, ids)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "content": doc,
                    "metadata": metadata,
                    "original_id": doc_id
                }
            )
            points.append(point)
            
            if (i + 1) % 100 == 0:
                print(f"📝 Prepared {i + 1}/{len(documents)} points...")
        
        # Upload to Qdrant in batches
        print("⬆️ Uploading to Qdrant Cloud...")
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=batch
            )
            print(f"✅ Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
        
        print(f"🎉 Successfully migrated {len(documents)} documents to Qdrant Cloud!")
        print(f"🔗 Collection URL: {QDRANT_URL}/collections/{COLLECTION_NAME}")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return

if __name__ == "__main__":
    migrate_to_qdrant()
