#!/usr/bin/env python3
"""
Test Qdrant Cloud connection
"""

from qdrant_client import QdrantClient
import os

# Your Qdrant credentials
QDRANT_URL = "https://89e4ac41-0755-4091-86e0-7fcc0ee433c3.eu-west-2-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.ZYhFwT_ttEcSalVBZGAXE1gkhhHcQlGOcQWYXY2kL1w"

print("Testing Qdrant Cloud connection...")
print(f"URL: {QDRANT_URL}")
print(f"API Key: {QDRANT_API_KEY[:20]}...")

try:
    # Try with timeout
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=30
    )
    
    print("Client created successfully!")
    
    # Test connection
    collections = client.get_collections()
    print(f"Connection successful! Collections: {collections}")
    
except Exception as e:
    print(f"Connection failed: {e}")
    print("\nTrying alternative URL format...")
    
    # Try without https
    try:
        alt_url = QDRANT_URL.replace("https://", "")
        client = QdrantClient(
            url=alt_url,
            api_key=QDRANT_API_KEY,
            timeout=30
        )
        collections = client.get_collections()
        print(f"Alternative URL worked! Collections: {collections}")
    except Exception as e2:
        print(f"Alternative URL also failed: {e2}")
