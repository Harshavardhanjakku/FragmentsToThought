#!/usr/bin/env python3
"""
Simple database creation script without Unicode characters
"""

import os
import time
import shutil
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Configuration
DATA_PATH = "data"
CHROMA_PATH = "chroma"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def load_documents():
    print(f"[DEBUG] Loading documents from: {DATA_PATH}")
    loader = DirectoryLoader(DATA_PATH, glob="**/*.md")
    documents = loader.load()
    print(f"[DEBUG] Loaded {len(documents)} documents")
    return documents

def split_text(documents):
    print("[DEBUG] Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"[DEBUG] Created {len(chunks)} chunks")
    return chunks

def save_to_chroma(chunks):
    print("[DEBUG] Removing old Chroma DB if exists...")
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    
    print("[DEBUG] Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    
    print("[DEBUG] Creating Chroma DB...")
    db = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_PATH)
    
    print("[DEBUG] Persisting Chroma DB...")
    db.persist()
    
    print(f"[DEBUG] Successfully saved {len(chunks)} chunks to {CHROMA_PATH}")

def main():
    print("[DEBUG] Starting database creation...")
    
    # Load documents
    documents = load_documents()
    
    # Split into chunks
    chunks = split_text(documents)
    
    # Save to ChromaDB
    save_to_chroma(chunks)
    
    print("[DEBUG] Database creation completed!")

if __name__ == "__main__":
    main()
