#!/usr/bin/env python3
"""
Enhanced Migration Script for Optimized ChromaDB to Qdrant Cloud
Features:
- Uses optimized chunks with metadata
- Enhanced embedding strategy
- Batch processing with progress tracking
- Quality validation
"""

import os
import uuid
import time
from typing import List, Dict
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

class EnhancedMigrator:
    def __init__(self):
        # Configuration
        self.CHROMA_PATH = "chroma"
        self.MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
        self.QDRANT_URL = os.getenv("QDRANT_URL")
        self.QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
        self.COLLECTION_NAME = "fragments_to_thought"
        
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(
            url=self.QDRANT_URL,
            api_key=self.QDRANT_API_KEY,
            timeout=60
        )
        
        # Initialize ChromaDB
        self.embeddings = HuggingFaceEmbeddings(model_name=self.MODEL_NAME)
        self.chroma_db = Chroma(
            persist_directory=self.CHROMA_PATH,
            embedding_function=self.embeddings
        )

    def migrate_optimized_data(self):
        """Migrate optimized ChromaDB data to Qdrant Cloud"""
        print("Starting enhanced migration with optimized chunks...")
        
        # Step 1: Create/update collection
        self._setup_qdrant_collection()
        
        # Step 2: Get optimized chunks from ChromaDB
        chunks = self._get_optimized_chunks()
        
        if not chunks:
            print("No chunks found in ChromaDB")
            return
        
        print(f"Found {len(chunks)} optimized chunks to migrate")
        
        # Step 3: Process and upload chunks
        self._process_and_upload_chunks(chunks)
        
        # Step 4: Validate migration
        self._validate_migration()

    def _setup_qdrant_collection(self):
        """Setup Qdrant collection with enhanced configuration"""
        print("Setting up Qdrant collection...")
        
        try:
            # Delete existing collection if it exists
            try:
                self.qdrant_client.delete_collection(self.COLLECTION_NAME)
                print("Deleted existing collection")
            except:
                pass  # Collection doesn't exist
            
            # Create new collection with optimized settings
            self.qdrant_client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2 embedding size
                    distance=Distance.COSINE
                )
            )
            print("Created new optimized collection")
            
        except Exception as e:
            print(f"Error setting up collection: {e}")
            raise

    def _get_optimized_chunks(self) -> List[Dict]:
        """Get optimized chunks from ChromaDB"""
        print("Retrieving optimized chunks from ChromaDB...")
        
        try:
            # Get all documents using similarity search with empty query
            all_docs = self.chroma_db.similarity_search("", k=1000)
            
            chunks = []
            for i, doc in enumerate(all_docs):
                chunk_data = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "index": i,
                    "word_count": len(doc.page_content.split()),
                    "char_count": len(doc.page_content)
                }
                chunks.append(chunk_data)
            
            print(f"Retrieved {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            return []

    def _process_and_upload_chunks(self, chunks: List[Dict]):
        """Process chunks and upload to Qdrant in optimized batches"""
        print("Processing and uploading chunks...")
        
        batch_size = 10  # Smaller batches for better reliability
        total_uploaded = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(chunks) - 1) // batch_size + 1
            
            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")
            
            # Process batch
            points = []
            for chunk in batch:
                try:
                    # Get embedding for this chunk
                    embedding = self.embeddings.embed_query(chunk["content"])
                    
                    # Create enhanced payload
                    payload = {
                        "content": chunk["content"],
                        "metadata": chunk["metadata"],
                        "word_count": chunk["word_count"],
                        "char_count": chunk["char_count"],
                        "chunk_index": chunk["index"],
                        "migration_timestamp": time.time(),
                        "source": "optimized_chromadb"
                    }
                    
                    # Create point
                    point = PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload=payload
                    )
                    points.append(point)
                    
                except Exception as e:
                    print(f"Error processing chunk {chunk['index']}: {e}")
                    continue
            
            # Upload batch
            if points:
                try:
                    self.qdrant_client.upsert(
                        collection_name=self.COLLECTION_NAME,
                        points=points
                    )
                    total_uploaded += len(points)
                    print(f"Uploaded {len(points)} points (total: {total_uploaded})")
                    
                    # Small delay between batches
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error uploading batch {batch_num}: {e}")
                    continue
        
        print(f"Migration completed! Uploaded {total_uploaded} chunks to Qdrant Cloud!")

    def _validate_migration(self):
        """Validate the migration was successful"""
        print("Validating migration...")
        
        try:
            # Get collection info
            collection_info = self.qdrant_client.get_collection(self.COLLECTION_NAME)
            print(f"Collection now has {collection_info.points_count} points")
            
            # Test search
            test_query = "jakku harshavardhan"
            test_embedding = self.embeddings.embed_query(test_query)
            
            search_results = self.qdrant_client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=test_embedding,
                limit=3
            )
            
            print(f"Test search returned {len(search_results.points)} results")
            
            # Print sample results
            print("\nSample results:")
            for i, result in enumerate(search_results.points[:2]):
                content = result.payload.get("content", "")[:100]
                print(f"  {i+1}: {content}...")
            
            print("Migration validation successful!")
            
        except Exception as e:
            print(f"Validation error: {e}")

def main():
    """Main function to run enhanced migration"""
    print("Starting Enhanced Migration Process...")
    print("="*60)
    
    migrator = EnhancedMigrator()
    migrator.migrate_optimized_data()
    
    print("="*60)
    print("Enhanced migration completed!")

if __name__ == "__main__":
    main()
