from fastapi import FastAPI, Request
from pydantic import BaseModel
from groqchat import get_answer_from_groq
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

app = FastAPI()

CHROMA_PATH = "chroma"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load DB
db = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=HuggingFaceEmbeddings(model_name=MODEL_NAME)
)

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(data: QuestionRequest):
    results = db.similarity_search(data.question, k=3)
    if not results:
        return {"answer": "I don't know based on the provided context."}
    
    context = "\n".join([doc.page_content for doc in results])
    answer = get_answer_from_groq(context, data.question)
    return {"answer": answer}
