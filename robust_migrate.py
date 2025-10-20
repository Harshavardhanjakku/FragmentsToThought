#!/usr/bin/env python3
"""
Robust migration script with better error handling and smaller batches
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import uuid
import time

load_dotenv()

# Configuration
CHROMA_PATH = "chroma"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "fragments_to_thought"

def robust_migrate():
    """Robust migration with better error handling"""
    
    print("Starting robust migration...")
    
    # Initialize Qdrant client with timeout
    print("Connecting to Qdrant Cloud...")
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=30
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
        
        # Get documents using similarity search
        print("Retrieving documents...")
        all_docs = chroma_db.similarity_search("", k=1000)
        
        if not all_docs:
            print("No documents found in ChromaDB")
            return
        
        print(f"Found {len(all_docs)} documents to migrate")
        
        # Process documents in very small batches
        batch_size = 5  # Very small batches to avoid timeouts
        total_uploaded = 0
        
        for i in range(0, len(all_docs), batch_size):
            batch_docs = all_docs[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(all_docs)-1)//batch_size + 1}")
            
            # Prepare points for this batch
            points = []
            for j, doc in enumerate(batch_docs):
                try:
                    # Get embedding for this document
                    doc_embedding = embeddings.embed_query(doc.page_content)
                    
                    point = PointStruct(
                        id=str(uuid.uuid4()),
                        vector=doc_embedding,
                        payload={
                            "content": doc.page_content,
                            "metadata": doc.metadata,
                            "original_id": f"doc_{i+j}"
                        }
                    )
                    points.append(point)
                    
                except Exception as e:
                    print(f"Error processing document {i+j}: {e}")
                    continue
            
            # Upload this batch
            if points:
                try:
                    qdrant_client.upsert(
                        collection_name=COLLECTION_NAME,
                        points=points
                    )
                    total_uploaded += len(points)
                    print(f"Uploaded {len(points)} points (total: {total_uploaded})")
                    
                    # Small delay between batches
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error uploading batch: {e}")
                    continue
        
        print(f"Migration completed! Uploaded {total_uploaded} documents to Qdrant Cloud!")
        
        # Verify upload
        try:
            collection_info = qdrant_client.get_collection(COLLECTION_NAME)
            print(f"Collection now has {collection_info.points_count} points")
        except Exception as e:
            print(f"Could not verify collection: {e}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    robust_migrate()
