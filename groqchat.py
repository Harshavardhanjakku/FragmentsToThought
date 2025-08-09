# groqchat.py
import os
from dotenv import load_dotenv
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in environment (.env or env vars)")

client = Groq(api_key=GROQ_API_KEY)

# Config
CHROMA_PATH = "chroma"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama3-8b-8192"

# Initialize Chroma once
db = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=HuggingFaceEmbeddings(model_name=MODEL_NAME)
)

def get_answer_from_groq(context: str, question: str) -> str:
    prompt = f"""
You are a highly knowledgeable assistant trained to answer based **strictly** on the given context. 

CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
- If the context is relevant, give a complete, clear answer.
- If the context is vague or doesn't have the answer, respond only with: "I don't know based on the provided context."
"""
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You're an AI assistant that answers strictly based on the context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=512
        )
        # adapt if SDK response shape is slightly different
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR] Failed to generate response from Groq: {e}"

def generate_answer(question: str, k: int = 3) -> str:
    """
    High-level API: runs similarity search and asks the LLM for an answer.
    Returns a string (answer) in all cases (or an error message string).
    """
    try:
        results = db.similarity_search(question, k=k)
    except Exception as e:
        return f"[ERROR] Vector search failed: {e}"

    if not results:
        return "I don't know based on the provided context."

    # build context from top results
    context = "\n\n".join([doc.page_content for doc in results if getattr(doc, "page_content", None)])
    return get_answer_from_groq(context.strip(), question)

# keep CLI for debugging
if __name__ == "__main__":
    print("[INFO] Running groqchat CLI. Type 'exit' to quit.")
    while True:
        q = input("\n❓ Ask: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        print("\n[INFO] Searching and generating...\n")
        print(generate_answer(q))
