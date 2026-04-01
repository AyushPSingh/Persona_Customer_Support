# 🤖 Persona-Adaptive Customer Support Agent

A stateful, LLM-powered customer support system that **automatically detects the customer's persona** and **adapts its response tone** accordingly. Built with LangGraph, LangChain, Groq, FAISS, and Streamlit.

---

## 📸 Architecture

```
User Input
    │
    ▼
┌─────────────────────┐
│  Persona Detection  │  ← Zero-shot LLM classification
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Context Retrieval  │  ← RAG: FAISS + HuggingFace Embeddings
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Response Generation │  ← Groq LLM + Tone instruction
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Escalation Check   │  ← Keyword-based human handoff
└─────────────────────┘
    │
    ▼
 Final Response
```

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| **Persona Detection** | Classifies users as **Technical Expert**, **Frustrated User**, or **Business Executive** using a zero-shot LLM prompt |
| **Tone Adaptation** | Injects persona-specific tone instructions into the system prompt for tailored responses |
| **RAG Knowledge Base** | Uses FAISS + sentence-transformers to retrieve relevant KB articles for accurate answers |
| **Smart Escalation** | Scans for high-risk keywords (e.g., "lawsuit", "unacceptable") to flag cases for human agents |
| **Stateful Orchestration** | Managed by LangGraph for clean, auditable pipeline transitions |
| **Multi-turn Memory** | Full conversation history is passed to the LLM for coherent multi-turn conversations |

---

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
git clone https://github.com/<your-username>/Persona_Customer_Support.git
cd Persona_Customer_Support
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API key

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

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

## 🧪 Example Interactions

### Technical Expert
> *"How do I authenticate my API requests and handle 429 rate-limit errors?"*

→ Agent responds with precise JWT token flow, rate-limit specifics, and `Retry-After` header guidance.

### Frustrated User
> *"I've been charged twice this month and nobody is helping me! This is unacceptable!"*

→ Agent responds empathetically, acknowledges frustration, provides step-by-step billing resolution, **and escalates to a human agent**.

### Business Executive
> *"What SLA does the Enterprise plan guarantee and what's the ROI?"*

→ Agent responds with a concise, outcome-focused summary of uptime guarantees, SLA credits, and plan benefits.

---

## 📁 Project Structure

```
Persona_Customer_Support/
├── app.py              # Streamlit UI
├── agent.py            # LangGraph pipeline assembly & entry-point
├── nodes.py            # The 4 pipeline nodes (detection, retrieval, generation, escalation)
├── agent_state.py      # Shared TypedDict state schema
├── vector_store.py     # FAISS vector store builder & retriever
├── knowledge_base.py   # KB articles (13 articles across billing/technical/account)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── .gitignore
```

---

## 🔄 How It Works

1. **Persona Detection Node** — A zero-shot LLM classification prompt categorises the user's message into one of three personas.
2. **Context Retrieval Node** — The user query is embedded and matched against the FAISS index of KB articles (top-3 retrieved).
3. **Response Generation Node** — The LLM generates a response using the KB context + a persona-specific tone instruction injected into the system prompt.
4. **Escalation Check Node** — The user message is scanned for ~15 high-risk keywords. If found, a human-handoff note is appended to the response.

---

## 📄 License

MIT
