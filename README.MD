# FinWise AI

> Enterprise-grade Financial Intelligence Assistant powered by Hybrid RAG, Redis Caching, and LLM Orchestration

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Redis](https://img.shields.io/badge/Redis-Caching-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![RAG](https://img.shields.io/badge/RAG-Hybrid-orange)
![Version](https://img.shields.io/badge/version-v0.1.0-brightgreen)

FinWise AI is a backend-first financial assistant designed to answer banking policy questions, explain financial concepts, and perform EMI calculations using a modular AI architecture.

The project combines Retrieval-Augmented Generation (RAG), Redis-powered caching, conversation memory, and orchestration patterns commonly used in production AI systems.

---

## Features

### Policy RAG

Ask questions about banking policies and receive grounded answers from source documents.

Examples:

* What is SBI's LTV ratio?
* Compare SBI and HDFC home loan eligibility.
* What are the foreclosure charges for HDFC loans?

### Hybrid Retrieval Pipeline

Instead of relying on vector search alone, FinWise uses:

* Vector Similarity Search
* BM25 Lexical Search
* Reciprocal Rank Fusion (RRF)
* Cross-Encoder Reranking

This improves retrieval quality for real-world banking documents.

### Financial Concept Explanations

Examples:

* What is SIP?
* What is inflation?
* What is compounding?
* What is a debt fund?

### EMI Calculator

Custom EMI calculations from user-provided inputs.

Example:

> I want to buy a phone worth ₹60,000 at 17% interest for 12 months.

FinWise calculates:

* Monthly EMI
* Total Payment
* Total Interest Paid

### Conversation Memory

The system maintains conversation context through:

* Recent Message Memory
* Long-Term Summary Memory

### Redis Caching

#### Summary Cache

Reduces repeated PostgreSQL reads for conversation summaries.

#### Response Cache

Caches generated responses to avoid repeated LLM execution for identical requests.

### Async Background Summarization

Conversation summaries are generated asynchronously after user responses are returned, improving latency and user experience.

---

## Architecture

```text
User
 │
 ▼
FastAPI API Layer
 │
 ▼
Orchestrator
 │
 ├── Intent Classification
 │
 ├── Policy RAG
 │     ├── Vector Search
 │     ├── BM25 Search
 │     ├── RRF Fusion
 │     └── Cross Encoder Reranker
 │
 ├── EMI Calculation
 │
 └── Explanation Generation
 │
 ▼
Response Generation
 │
 ▼
Redis Response Cache
 │
 ▼
Conversation Storage
 │
 ▼
Background Summary Generation
 │
 ▼
Redis Summary Cache
```

---

## Technology Stack

### Backend

* FastAPI
* Python 3.11+

### Database

* PostgreSQL
* AsyncPG

### Caching

* Redis

### LLM Layer

* Ollama
* Llama 3.2

### RAG Stack

* ChromaDB
* Sentence Transformers
* BM25
* Cross Encoder Reranker

### AI Frameworks

* LangChain
* LangGraph

### Evaluation

* DeepEval

---

## Current Project Structure

```text
src/app
├── api/
├── auth/
├── cache/
├── infra/
├── memory/
├── nodes/
├── orchestration/
├── services/
├── tasks/
└── utils/
```

---

## Performance Optimizations

### Hybrid Retrieval

Combines semantic and lexical search for improved recall.

### Reciprocal Rank Fusion

Merges retrieval results from multiple retrievers.

### Cross Encoder Reranking

Improves precision before answer generation.

### Redis Summary Cache

Avoids unnecessary database reads.

### Redis Response Cache

Avoids repeated LLM execution.

### Async Background Processing

Moves conversation summarization outside the request path.

---

## Example Queries

### Policy Questions

* What is SBI home loan LTV ratio?
* Compare SBI and HDFC home loan policies.
* What are the processing charges for HDFC loans?

### Financial Concepts

* What is SIP?
* What is inflation?
* What is compounding?
* What is an ETF?

### EMI Calculations

* Calculate EMI for ₹5 lakh at 11% interest for 5 years.
* Calculate EMI for a ₹60,000 phone at 17% interest for 12 months.

---

## Running Locally

### Clone Repository

```bash
git clone https://github.com/parthib01/finwise-ai.git
cd finwise-ai
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate

Windows:

```bash
.venv\Scripts\activate
```

Linux / Mac:

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -e .
```

### Start PostgreSQL

Ensure PostgreSQL is running.

### Start Redis

```bash
docker start finwise-redis
```

### Start Ollama

```bash
ollama serve
```

Pull model:

```bash
ollama pull llama3.2:3b
```

### Run Application

```bash
uvicorn app.main:app --reload
```

---

## API Documentation

Swagger UI:

```text
http://localhost:8000/docs
```

---

## Roadmap

### Completed

* Authentication & Sessions
* Conversation Management
* Policy RAG
* Hybrid Retrieval
* BM25 Search
* RRF Fusion
* Cross Encoder Reranking
* EMI Calculator
* Conversation Memory
* Redis Summary Cache
* Redis Response Cache
* Async Summary Generation

### In Progress

* Retrieval Cache
* Dockerization
* Docker Compose

### Planned

* Kubernetes Deployment
* CI/CD Pipelines
* Monitoring & Observability
* User Document Uploads
* Advanced Financial Analytics

---

## Version

Current Release:

```text
v0.1.0
```

---

## Author

Parthib Banerjee

Software Engineer focused on AI Engineering, Retrieval-Augmented Generation (RAG), LLM Systems, and Enterprise AI Applications.