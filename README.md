# 🤖 Agentic Customer Support AI

An intelligent, production-ready customer support chatbot built with **LangGraph**, **FastAPI**, **Streamlit**, and **Redis**. The agent uses a multi-node pipeline to classify, route, retrieve, and respond to customer queries — all in real-time via streaming.

---

## 📋 Table of Contents

- [Architecture Overview](#-architecture-overview)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Agent Pipeline](#-agent-pipeline)
- [Features](#-features)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Running the Project](#-running-the-project)
- [API Reference](#-api-reference)

---

## 🏗️ Architecture Overview

```
User (Streamlit UI)
        │
        ▼
FastAPI /chat endpoint   ◄─── Rate Limiter (Redis, 5 req/60s per IP)
        │
        ▼
   LangGraph Pipeline
        │
  ┌─────┴──────────────────────────────────────────────┐
  │  Guard → Classify → EntityExtractor → Retriever    │
  │                                    → Tool          │
  │                                    → Generator     │
  └────────────────────────────────────────────────────┘
        │
  Redis (RedisSaver) ◄── Persistent conversation memory per thread_id
        │
        ▼
  Streaming Response back to Streamlit
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Groq · `llama-3.3-70b-versatile` |
| **Agent Orchestration** | LangGraph (StateGraph) |
| **RAG - Embeddings** | HuggingFace · `BAAI/bge-base-en-v1.5` |
| **RAG - Vector Store** | Qdrant Cloud |
| **Backend API** | FastAPI + Uvicorn |
| **Frontend** | Streamlit |
| **Memory** | Redis Stack (RedisSaver — persistent across restarts) |
| **Rate Limiting** | Redis (5 requests per 60 seconds per IP) |
| **Observability** | Langfuse |
| **Containerization** | Docker + Docker Compose |

---

## 📁 Project Structure

```
.
├── app/
│   ├── agents/
│   │   ├── graph.py              # LangGraph orchestrator — compiles the full pipeline
│   │   ├── state.py              # AgentState TypedDict (shared across all nodes)
│   │   ├── router.py             # Conditional edge logic after entity extraction
│   │   ├── nodes/
│   │   │   ├── guard_node.py     # LLM-based safety classifier (support/blocked/injection)
│   │   │   ├── classify_node.py  # Classifies ticket → category, urgency, action, tool_name
│   │   │   ├── entity_node.py    # Extracts order_id, ticket_id, user_id from message
│   │   │   ├── retriever_node.py # Runs RAG retrieval from Qdrant
│   │   │   ├── tool_node.py      # Executes mock DB tools (orders, tickets, users)
│   │   │   └── generater_node.py # Builds final prompt and calls LLM
│   │   └── tools/
│   │       ├── order_tool.py     # track_order, cancel_order, check_return_eligibility
│   │       ├── ticket_tool.py    # check_ticket_status, get_ticket
│   │       └── user_tool.py      # get_user
│   ├── rag/
│   │   ├── loader.py             # Loads knowledge base + resolved tickets JSON
│   │   ├── chunk.py              # Splits documents into chunks
│   │   ├── embedding.py          # HuggingFace embedding model wrapper
│   │   ├── qdrant.py             # Qdrant Cloud client (creates/uploads collection)
│   │   ├── retriever.py          # Qdrant similarity search retriever
│   │   ├── generate.py           # Generator: stream_generate() for streaming responses
│   │   ├── llm.py                # ChatGroq LLM factory
│   │   └── bm25.py               # BM25 retriever (optional hybrid search)
│   ├── middleware/
│   │   └── rate_limiter.py       # Redis-based rate limiting middleware (5 req/60s)
│   ├── prompts/                  # All LLM prompts (classify, entity, generate, guard)
│   ├── schema/                   # Pydantic schemas for structured LLM outputs
│   ├── config/
│   │   └── config.py             # All env var loading and constants
│   ├── api.py                    # FastAPI app, /chat streaming endpoint
│   └── main.py                   # Streamlit UI with multi-chat sidebar
├── support-agent-data/
│   ├── knowledge_base/           # Policy docs, FAQs, resolved tickets
│   ├── mock_db/                  # JSON mock database (orders, tickets, users, tracking)
│   │   ├── orders.json           # Mock order data
│   │   ├── tickets.json          # Enriched mock tickets with full conversation history
│   │   ├── tracking.json         # Realistic package tracking events (FedEx, UPS, etc.)
│   │   └── users.json            # Mock user profiles
├── tests/
│   ├── test_agent.py
│   ├── test_graph.py
│   ├── test_rag_pipeline.py
│   └── test_tool_nodes.py
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
└── .env
```

---

## 🔀 Agent Pipeline

Every user message travels through this exact pipeline:

### 1. `Guard Node`
- **Type:** LLM classifier (Groq, temperature=0)
- **Purpose:** Safety gate — classifies message as `support`, `blocked`, or `injection`
- Blocked messages are short-circuited directly to the Generator with a canned refusal response
- Injection attempts (prompt jailbreaks) are also blocked immediately

### 2. `Classify Node`
- **Type:** LLM with structured output (`ClassificationSchema`)
- **Extracts:** `category`, `urgency`, `sentiment`, `action`, `tool_name`
- **Action options:** `retrieve`, `call_tool`, `clarify`, `escalate`, `respond`

### 3. `Entity Extractor Node`
- **Type:** LLM with structured output (`EntitySchema`)
- **Extracts:** `order_id`, `ticket_id`, `user_id` from the user's message
- Looks at the last 4 messages of history to catch IDs mentioned earlier in the conversation

### 4. Router (Conditional Edge)
- Routes to one of three paths based on the `action` from Classify:
  - `retrieve` → **Retriever Node** (RAG/FAQ)
  - `call_tool` → **Tool Node** (live DB lookup)
  - `clarify` / `escalate` / `respond` → **Generator Node** (direct reply)

### 5a. `Retriever Node`
- Queries Qdrant Cloud with the user's message
- Returns the top-k most relevant policy/FAQ document chunks

### 5b. `Tool Node`
- Executes one of 6 mock DB tools based on `tool_name`:
  - `track_order`, `cancel_order`, `check_return_eligibility`
  - `check_ticket_status`, `get_ticket`, `get_user`

### 6. `Generator Node`
- Builds the final prompt combining: ticket, action, history, documents, tool results
- Calls Groq LLM and **streams tokens** back to the FastAPI endpoint

---

## ✨ Features

| Feature | Implementation | Status |
|---|---|---|
| 🛡️ Safety Guard | LLM-based (blocks off-topic + injection attacks) | ✅ Active |
| 🔀 Smart Routing | 5 routing paths based on intent classification | ✅ Active |
| 🔍 Hybrid RAG | Qdrant Cloud dense + BM25 sparse ensemble retrieval | ✅ Active |
| 🔧 Tool Calling | 6 structured tools for order/ticket/user lookups | ✅ Active |
| 💬 Streaming | Real-time token streaming (`StreamingResponse`) | ✅ Active |
| 🧠 Persistent Memory | Redis Stack (`RedisSaver`) — survives server restarts | ✅ Active |
| 🚦 Rate Limiting | Redis middleware — 5 requests / 60 seconds per IP | ✅ Active |
| 🚀 CI/CD Pipeline | Automated GitHub Actions deployment to AWS EC2 | ✅ Active |
| 🔭 Observability | Langfuse tracing (toggleable via `LANGFUSE_ENABLED`) | ✅ Active |
| 📦 Realistic Data | Enriched `tickets.json` histories and chronologic `tracking.json` events | ✅ Active |
| 🐳 Docker | Full docker-compose stack (Redis + API + UI) | ✅ Active |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A [Groq API key](https://console.groq.com/)
- A [Qdrant Cloud](https://cloud.qdrant.io/) cluster URL and API key

### 1. Clone and set up environment

```bash
git clone <your-repo-url>
cd <project-folder>

python -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 2. Create your `.env` file

```bash
cp .env.example .env
# then fill in your keys (see Environment Variables section below)
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
# Required
GROQ_API_KEY=gsk_...

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key

# Redis (auto-handled by docker-compose, only needed for local dev)
REDIS_URL=redis://localhost:6379

# Optional: Langfuse Observability
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://us.cloud.langfuse.com
LANGFUSE_ENABLED=true
```

---

## ▶️ Running the Project

### Option A — Docker Compose (Recommended)

Runs everything (Redis, FastAPI, Streamlit) in one command:

```bash
docker-compose up --build -d
```

| Service | URL |
|---|---|
| Streamlit UI | http://localhost:8501 |
| FastAPI API | http://localhost:8000 |
| Redis UI (RedisInsight) | http://localhost:8001 |

To stop everything:
```bash
docker-compose down
```

---

### Option C — AWS EC2 Deployment (Automated via CI/CD)

The project includes a fully automated **GitHub Actions** pipeline (`.github/workflows/deploy.yml`) that deploys directly to an AWS EC2 instance.

For detailed instructions on setting up the EC2 server (including Swap File configuration for the Free Tier) and configuring the required GitHub Secrets (`EC2_HOST`, `EC2_USERNAME`, `EC2_SSH_KEY`, `ENV_FILE`), please refer to the [AWS Deployment Guide](AWS_DEPLOYMENT.md).

Once configured, any push to the `main` branch will automatically deploy the latest changes to your live server.

---

### Option B — Local Development

Run 3 separate terminals:

**Terminal 1 — Redis Stack**
```bash
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

**Terminal 2 — FastAPI Backend**
```bash
source venv/bin/activate
uvicorn app.api:app --reload
```

**Terminal 3 — Streamlit Frontend**
```bash
source venv/bin/activate
streamlit run app/main.py
```

---

## 📡 API Reference

### `POST /chat`

Streams a response from the support agent.

**Request body:**
```json
{
  "ticket": "My order ORD-1011 is missing",
  "thread_id": "unique-session-id"
}
```

**Response:** `text/plain` stream (chunked tokens)

**Rate limit:** 5 requests per 60 seconds per IP → returns `HTTP 429` when exceeded.

**Example:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"ticket": "Where is my order ORD-1011?", "thread_id": "test-123"}'
```

---

## 🧪 Running Tests

```bash
source venv/bin/activate
pytest tests/ -v
```
