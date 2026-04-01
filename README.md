# Persona-Adaptive Customer Support Agent

A stateful, LLM-powered customer support system that **automatically detects the customer's persona** and **adapts its response tone** accordingly. Built with LangGraph, LangChain, Groq, FAISS, and Streamlit.

## 🛠️ Tech Stack

- **Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph)
- **Framework**: [LangChain](https://python.langchain.com/)
- **LLM**: [Groq](https://groq.com/) (Llama 3 8B)
- **Vector Store**: [FAISS](https://github.com/facebookresearch/faiss)
- **Embeddings**: HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
- **UI**: [Streamlit](https://streamlit.io/)

---

## ⚙️ Setup & Installation

### 1. Prerequisites

- Python 3.9 or higher
- A free [Groq API key](https://console.groq.com/)

### 2. Clone the repository

```bash
git clone https://github.com/AyushPSingh/Persona_Customer_Support.git
cd Persona_Customer_Support
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API key

Create a `.env` file by renaming the env example file in the root directory:

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=gsk_your_key_here
```

### 5. Run the application

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---



## How It Works

1. **Persona Detection Node** — A zero-shot LLM classification prompt categorises the user's message into one of three personas.
2. **Context Retrieval Node** — The user query is embedded and matched against the FAISS index of KB articles (top-3 retrieved).
3. **Response Generation Node** — The LLM generates a response using the KB context + a persona-specific tone instruction injected into the system prompt.
4. **Escalation Check Node** — The user message is scanned for ~15 high-risk keywords. If found, a human-handoff note is appended to the response.


