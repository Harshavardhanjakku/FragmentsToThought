#!/usr/bin/env python3
"""
Check Qdrant collection contents
"""

from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "fragments_to_thought"

def check_collection():
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    # Get collection info
    info = client.get_collection(COLLECTION_NAME)
    print(f"Collection has {info.points_count} points")
    
    # Get sample results
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=[0.1] * 384,  # Dummy query
        limit=3
    )
    
    print(f"\nSample results ({len(results.points)}):")
    for i, result in enumerate(results.points):
        content = result.payload.get("content", "")
        print(f"\nResult {i+1}:")
        print(f"Content: {content[:200]}...")
        print(f"Metadata: {result.payload.get('metadata', {})}")

if __name__ == "__main__":
    check_collection()
