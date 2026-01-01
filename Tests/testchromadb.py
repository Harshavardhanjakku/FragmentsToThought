from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

db = Chroma(
    persist_directory="chroma",
    embedding_function=HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
)

print(len(db.get()["documents"]))
