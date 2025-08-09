from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_PATH = "chroma"

def query_chroma():
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    )
    while True:
        question = input("\n❓ Ask a question (or type 'exit'): ")
        if question.lower() == "exit":
            break

        results = db.similarity_search(question, k=3)
        print("\n📚 Top Matches:")
        for i, doc in enumerate(results, 1):
            print(f"\nMatch {i}: {doc.page_content} (Source: {doc.metadata})")

if __name__ == "__main__":
    query_chroma()
