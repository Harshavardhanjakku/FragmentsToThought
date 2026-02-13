from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Resolve absolute path to project root's chroma directory
BASE_DIR = Path(__file__).resolve().parents[1]
CHROMA_PATH = BASE_DIR / "chroma"

db = Chroma(
    persist_directory=str(CHROMA_PATH),
    embedding_function=HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
)

print(f"Chroma DB path: {CHROMA_PATH}")
print(f"Total documents: {len(db.get()['documents'])}")
