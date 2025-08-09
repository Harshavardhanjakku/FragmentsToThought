 # 🌌 EchoesOfKnowledge

> **"Fragments of thought, reassembled into clarity."**

A lightning-fast **Retrieval-Augmented Generation (RAG)** chatbot built with **Groq LLM**, **semantic embeddings**, and **chunked knowledge bases**.  
It retrieves precise information from your data using **Chroma vector search**, then crafts answers *strictly based on the provided context* — never hallucinating beyond it.

---

## 🚀 Features

- **Groq-Powered Responses** – Blazing inference speed with `llama3-8b-8192`.
- **Strict Context Awareness** – Only answers if relevant info exists in your data.
- **Smart Chunking** – Markdown-aware splitting + optimized chunk sizes for better retrieval.
- **Semantic Search** – `sentence-transformers/all-MiniLM-L6-v2` for high-quality embeddings.
- **CLI Debug Mode** – Ask and test directly in your terminal.
- **Modular Architecture** – Easy to extend for APIs or UI chatbots.

---

## 📂 Project Structure

```

mychatbotbackend/
│
├── chroma/                  # Persisted Chroma vector store
├── data/                     # Your source documents (Markdown, text, etc.)
│
├── create\_database.py        # Loads docs → chunks → embeds → saves to Chroma
├── groqchat.py               # Retrieves context & queries Groq LLM
├── query\_data.py             # Query interface for testing retrieval
├── compare\_embeddings.py     # Compare & debug embeddings
├── server.py                 # (Optional) Backend server to expose chatbot API
│
├── requirements.txt          # Python dependencies
└── .env                      # API keys (not committed)

````

---

## ⚙️ Setup

### 1️⃣ Clone the Repo
```bash
git clone https://github.com/YOUR-USERNAME/EchoesOfKnowledge.git
cd EchoesOfKnowledge
````

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Add Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 📚 Usage

### **Step 1: Build the Knowledge Base**

```bash
python create_database.py
```

This will:

* Load all documents from `data/`
* Chunk them intelligently
* Generate embeddings
* Save to `chroma/`

### **Step 2: Ask Questions via CLI**

```bash
python groqchat.py
```

Example:

```
❓ Ask: Who is Harsha ? Tell me about him 
[INFO] Searching and generating...

Answer: The chapter focuses on ...
```

### **Step 3: (Optional) Run as an API**

```bash
python server.py
```

Then send POST requests to `/ask` with a JSON body:

```json
{
  "question": "Explain about Jakku Harshavardhan Briefly"
}
```

---

## 🧠 How It Works

1. **Chunking** – Your documents are split into manageable sections with overlap for better semantic retrieval.
2. **Embeddings** – Each chunk is transformed into a vector using `sentence-transformers/all-MiniLM-L6-v2`.
3. **Vector Search** – The query is embedded and matched against the Chroma database.
4. **Groq LLM** – The top `k` results are passed to Groq's ultra-fast `llama3-8b-8192` model.
5. **Strict Context** – If no relevant info is found, the bot says `"I don't know based on the provided context."`

---

## 🛠 Tech Stack

* **LLM:** [Groq](https://groq.com/) (`llama3-8b-8192`)
* **Vector Store:** [Chroma](https://www.trychroma.com/)
* **Embeddings:** [HuggingFace Sentence Transformers](https://www.sbert.net/)
* **Document Loading & Splitting:** LangChain
* **Backend:** Python
* **Environment Management:** `python-dotenv`

---

## 💡 Example Use Cases

* **Enterprise Search** – Query company manuals, policies, or technical docs.
* **Education** – Summarize or answer questions from textbooks.
* **Knowledge Vault** – Build a private AI that knows only your curated information.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## ✨ Author

**Jakku Harshavardhan**
*Fragments gathered, meaning restored.*

```
t banner?
```
