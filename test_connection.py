#!/usr/bin/env python3
"""
Test Qdrant connection with timeout handling
"""

from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "fragments_to_thought"

def test_connection():
    print("Testing Qdrant connection with timeout...")
    
    try:
        # Create client with timeout
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=10  # 10 second timeout
        )
        
        print("Client created successfully!")
        
        # Test basic connection
        collections = client.get_collections()
        print(f"Collections: {collections}")
        
        # Test if our collection exists
        try:
            collection_info = client.get_collection(COLLECTION_NAME)
            print(f"Collection '{COLLECTION_NAME}' exists: {collection_info}")
        except Exception as e:
            print(f"Collection '{COLLECTION_NAME}' not found: {e}")
        
        # Test a simple query with dummy vector
        dummy_vector = [0.1] * 384  # 384-dimensional vector
        try:
            results = client.query_points(
                collection_name=COLLECTION_NAME,
                query=dummy_vector,
                limit=1
            )
            print(f"Query test successful: {len(results.points)} results")
        except Exception as e:
            print(f"Query test failed: {e}")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
