# 📂 create_database.py (FINAL VERSION with Markdown-aware chunking + improved chunk sizes)

from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil
import time

CHROMA_PATH = "chroma"
DATA_PATH = "data/books"


def main():
    print("[DEBUG] 🚀 Script started.")
    start_time = time.time()

    generate_data_store()

    print(f"[DEBUG] ✅ Script finished in {time.time() - start_time:.2f} seconds.")


def generate_data_store():
    print("[DEBUG] 📥 Calling load_documents()...")
    documents = load_documents()
    print(f"[DEBUG] ✅ Loaded {len(documents)} document(s).")

    print("[DEBUG] ✂️ Calling split_text()...")
    chunks = split_text(documents)
    print(f"[DEBUG] ✅ Received {len(chunks)} chunk(s) after splitting.")

    print("[DEBUG] 💾 Calling save_to_chroma()...")
    save_to_chroma(chunks)
    print("[DEBUG] ✅ Data successfully saved to Chroma.")


def load_documents():
    print(f"[DEBUG] 📂 Initializing DirectoryLoader with path: {DATA_PATH}")
    loader = DirectoryLoader(DATA_PATH, glob="test.md")

    print("[DEBUG] 🔍 DirectoryLoader initialized. Calling .load()...")
    load_start = time.time()
    documents = loader.load()
    print(f"[DEBUG] ✅ Document loading completed in {time.time() - load_start:.2f} sec.")

    print(f"[DEBUG] 📄 Total documents loaded: {len(documents)}")
    if documents:
        print("[DEBUG] 📑 Sample document content (first 100 chars):")
        print(documents[0].page_content[:100])
        print("[DEBUG] 🏷 Sample document metadata:")
        print(documents[0].metadata)

    # ✅ Optional: Clean extra whitespace
    for doc in documents:
        doc.page_content = doc.page_content.strip()

    return documents


def split_text(documents: list[Document]):
    print("[DEBUG] ✂️ Setting up MarkdownHeaderTextSplitter + RecursiveCharacterTextSplitter...")

    # ✅ Split first by Markdown headings
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
    )

    all_md_chunks = []
    for doc in documents:
        md_chunks = markdown_splitter.split_text(doc.page_content)
        for chunk in md_chunks:
            all_md_chunks.append(Document(page_content=chunk.page_content, metadata=doc.metadata))

    print(f"[DEBUG] ✅ Markdown split created {len(all_md_chunks)} section(s).")

    # ✅ Then split into character-based chunks (bigger chunks)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,     # increased from 300 → 1000
        chunk_overlap=200,   # increased from 100 → 200
        length_function=len,
        add_start_index=True,
    )

    print("[DEBUG] 🪓 Splitting Markdown sections into final chunks...")
    split_start = time.time()
    chunks = text_splitter.split_documents(all_md_chunks)
    print(f"[DEBUG] ✅ Splitting done in {time.time() - split_start:.2f} sec.")
    print(f"[DEBUG] 📊 {len(all_md_chunks)} md section(s) → {len(chunks)} chunk(s).")

    if chunks:
        print("[DEBUG] 📑 Sample chunk content (first 200 chars):")
        print(chunks[0].page_content[:200])
        print("[DEBUG] 🏷 Sample chunk metadata:")
        print(chunks[0].metadata)

    return chunks


def save_to_chroma(chunks: list[Document]):
    print("[DEBUG] 📦 Checking if Chroma DB already exists at:", CHROMA_PATH)
    if os.path.exists(CHROMA_PATH):
        print(f"[DEBUG] 🗑 Removing old Chroma DB at {CHROMA_PATH}...")
        shutil.rmtree(CHROMA_PATH)
    else:
        print("[DEBUG] ✅ No existing Chroma DB found, fresh start.")

    print("[DEBUG] 🤖 Initializing HuggingFaceEmbeddings...")
    embed_start = time.time()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print(f"[DEBUG] ✅ HuggingFace model loaded in {time.time() - embed_start:.2f} sec.")

    print("[DEBUG] 📥 Creating Chroma vector store...")
    try:
        chroma_start = time.time()
        print("[DEBUG] 🚧 Calling Chroma.from_documents() (this might take time)...")
        db = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_PATH)
        print(f"[DEBUG] ✅ Chroma DB created in {time.time() - chroma_start:.2f} sec.")
    except Exception as e:
        print(f"[ERROR] ❌ Failed to create Chroma DB: {str(e)}")
        exit(1)

    print("[DEBUG] 💾 Persisting Chroma DB (note: Chroma auto-saves, so this is quick)...")
    persist_start = time.time()
    db.persist()
    print(f"[DEBUG] ✅ Chroma DB persisted in {time.time() - persist_start:.2f} sec.")

    print(f"[DEBUG] 🎉 Saved {len(chunks)} chunk(s) to {CHROMA_PATH}.")


if __name__ == "__main__":
    print("[DEBUG] 🏁 __main__ entry point reached.")
    main()
