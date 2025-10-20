#!/usr/bin/env python3
"""
Simple migration script for ChromaDB to Qdrant Cloud
"""

import os
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

def simple_migrate():
    """Simple migration from ChromaDB to Qdrant Cloud"""
    
    print("Starting simple migration...")
    
    # Initialize Qdrant client
    print("Connecting to Qdrant Cloud...")
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
    
    # Create collection
    print(f"Creating collection '{COLLECTION_NAME}'...")
    try:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )
        print("Collection created successfully")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("Collection already exists, continuing...")
        else:
            print(f"Error creating collection: {e}")
            return
    
    # Load ChromaDB
    print("Loading ChromaDB...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        chroma_db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings
        )
        
        # Get documents using similarity search (more reliable)
        print("Retrieving documents using similarity search...")
        all_docs = chroma_db.similarity_search("", k=1000)  # Get all docs
        
        if not all_docs:
            print("No documents found in ChromaDB")
            return
        
        print(f"Found {len(all_docs)} documents to migrate")
        
        # Prepare points for Qdrant
        points = []
        for i, doc in enumerate(all_docs):
            # Get embedding for this document
            doc_embedding = embeddings.embed_query(doc.page_content)
            
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=doc_embedding,
                payload={
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "original_id": f"doc_{i}"
                }
            )
            points.append(point)
            
            if (i + 1) % 10 == 0:
                print(f"Prepared {i + 1}/{len(all_docs)} points...")
        
        # Upload to Qdrant
        print("Uploading to Qdrant Cloud...")
        batch_size = 50
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=batch
            )
            print(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
        
        print(f"Successfully migrated {len(all_docs)} documents to Qdrant Cloud!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_migrate()
