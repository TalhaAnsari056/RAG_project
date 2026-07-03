# 🤖 AI Policy Assistant (RAG Chatbot)

An AI-powered Retrieval-Augmented Generation (RAG) chatbot that answers questions from company policy documents using semantic search, vector embeddings, and locally hosted Large Language Models (LLMs) with Ollama.

---

## ✨ Features

- Semantic Search using ChromaDB
- Retrieval-Augmented Generation (RAG)
- Local LLM Inference with Ollama (Qwen)
- Intelligent Query Routing
- Greeting Agent
- PDF Knowledge Agent
- Scope Guard Agent
- OCR Support for Scanned PDFs
- Confidence Score
- Retrieved Chunks Display
- Runtime Metrics
- Similarity Score
- Pipeline Visualization
- Modern Interactive UI

---

## 🛠️ Tech Stack

### Backend
- Python
- Flask
- LangChain

### Vector Database
- ChromaDB

### Embedding Model
- sentence-transformers/all-MiniLM-L6-v2

### Large Language Model
- Ollama
- Qwen 2.5

### OCR
- Tesseract OCR

---

## 📂 Project Structure

```
RAG_PROJECT/
│
├── agents/
├── data/
├── static/
├── templates/
├── vectordb/
├── app.py
├── ingest.py
├── retriever.py
├── llm.py
├── prompts.py
├── config.py
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### Clone Repository

```bash
git clone <repository-url>
cd RAG_PROJECT
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

Windows

```bash
.venv\Scripts\activate
```

Linux/Mac

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Ollama

Download:

https://ollama.com/download

Pull the model:

```bash
ollama pull qwen2.5:3b
```

### Install Tesseract OCR

Download:

https://github.com/UB-Mannheim/tesseract/wiki

---

## Build Vector Database

```bash
python ingest.py
```

---

## Run Application

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

## Future Improvements

- Multi-PDF Support
- Conversation Memory
- Streaming Responses
- Hybrid Search
- Re-ranking
- Authentication
- Docker Deployment