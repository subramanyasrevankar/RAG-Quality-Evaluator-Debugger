# RAG Quality Evaluator & Debugger

> A full-stack tool that evaluates **why your RAG pipeline is failing** and tells you exactly which step broke — retrieval, generation, or context usage.

![RAG Quality Evaluator](https://img.shields.io/badge/RAG-Evaluator-4f46e5?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

---

## The Problem

Every team building RAG hits the same wall — bad answers, no idea where it broke.

- Was it the **retrieval**? Wrong chunks fetched?
- Was it the **LLM**? Hallucinating outside the context?
- Was it **context utilization**? Retrieved chunks ignored?

This tool gives you per-step scores and tells you **exactly what to fix.**

---

## Evaluation Metrics

| Metric | What it measures | Weight |
|---|---|---|
| **Retrieval Relevance** | Are the retrieved chunks related to the question? | 40% |
| **Answer Faithfulness** | Does the answer stick to what the chunks say? | 40% |
| **Context Utilization** | How much of the retrieved context was actually used? | 20% |

---

## Features

- Upload PDF, TXT, or MD documents
- Ask natural language questions
- Get per-step evaluation scores with letter grade (A-F)
- Auto-debugger suggests specific fixes based on which metric failed
- Hallucination detection using LLM-as-judge pattern
- Redis exact match + semantic similarity caching
- Analytics dashboard with score trend charts
- Query history with expandable answers
- CSV export for offline analysis
- Domain-specific templates (Research, Legal, Financial, Technical)

---

## Tech Stack

### Backend
- **FastAPI** — REST API
- **PostgreSQL + SQLAlchemy** — Persistent storage for evaluation runs
- **ChromaDB** — Vector store for document embeddings
- **Sentence Transformers** (`all-MiniLM-L6-v2`) — Local embeddings
- **Gemini API** (`gemini-1.5-flash`) — Answer generation + LLM-as-judge evaluation
- **Upstash Redis** — Exact match + semantic similarity caching

### Frontend
- **React + Vite** — UI framework
- **Recharts** — Score trend visualization
- **Lucide React** — Icons

---

## Architecture
User Query
│
▼
┌─────────────────────────────────────┐
│           FastAPI Backend            │
│                                     │
│  1. Check Redis exact cache         │
│  2. Check semantic similarity cache │
│  3. Retrieve chunks from ChromaDB   │
│  4. Score retrieval relevance       │
│  5. Generate answer (Gemini API)    │
│  6. Score faithfulness (local)      │
│  7. Score utilization (local)       │
│  8. LLM-as-judge faithfulness check │
│  9. Combine scores (40/40/20)       │
│  10. Auto-debug + suggest fixes     │
│  11. Save to PostgreSQL             │
│  12. Cache result in Redis          │
└─────────────────────────────────────┘
│
▼

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload and chunk a document |
| `POST` | `/query` | Ask a question + get full evaluation |
| `GET` | `/history` | Get past evaluation runs |
| `GET` | `/stats` | Get average scores |
| `GET` | `/templates` | Get domain templates |
| `GET` | `/export/csv` | Download evaluation history |
| `GET` | `/cache/stats` | Redis cache statistics |
| `DELETE` | `/cache/clear` | Clear all caches |

---

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL
- Node.js 18+

### Backend

```bash
# Clone the repo
git clone https://github.com/subramanyasrevankar/RAG-Quality-Evaluator-Debugger.git
cd RAG-Quality-Evaluator-Debugger

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Create PostgreSQL database
# In pgAdmin or psql: CREATE DATABASE rag_evaluator;

# Run the backend
python run.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag_evaluator
GEMINI_API_KEY=your_gemini_key_here
UPSTASH_REDIS_REST_URL=your_upstash_url
UPSTASH_REDIS_REST_TOKEN=your_upstash_token

---

## Phase-wise Development

| Phase | What was built |
|---|---|
| **Phase 1** | Core RAG pipeline — chunking, ChromaDB, retrieval relevance scorer |
| **Phase 2** | Gemini integration — answer generation, faithfulness + utilization scoring |
| **Phase 3** | React dashboard — Upload, Query, Analytics, History components |
| **Phase 4** | Redis caching — exact match + semantic similarity cache |
| **Phase 5** | Templates, auto-debugger, CSV export, UI improvements |

---

## Key Design Decisions

**Why cosine similarity for retrieval scoring?**
Cosine similarity measures the angle between embedding vectors — two chunks can be far apart in space but semantically similar. It's more reliable than dot product for normalized embeddings.

**Why 40/40/20 metric weights?**
Retrieval and faithfulness are the two biggest RAG failure modes — wrong chunks and hallucination. Utilization at 20% is a secondary signal. These weights reflect production RAG evaluation frameworks like RAGAS.

**Why LLM-as-judge for faithfulness?**
Local cosine similarity gives a fast baseline score. The Gemini judge call adds semantic understanding — it can detect subtle hallucinations that embedding similarity misses. Blending both (50/50) gives a more robust signal.

**Why Redis semantic caching?**
Exact match cache handles identical questions. Semantic cache handles near-duplicates like "What is ML?" vs "Explain machine learning" — saves API calls without compromising accuracy.

---

## Author

**Subramanya Srevankar**
- GitHub: [@subramanyasrevankar](https://github.com/subramanyasrevankar)
