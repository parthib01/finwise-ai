# FinWise AI

> Enterprise-grade Financial Intelligence Assistant powered by Hybrid RAG, Redis Caching, and LLM Orchestration.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Redis](https://img.shields.io/badge/Redis-Caching-red)
![RAG](https://img.shields.io/badge/RAG-Hybrid-orange)
![Version](https://img.shields.io/badge/version-v0.1.0-brightgreen)

---

# Overview

FinWise AI is a backend-first financial intelligence assistant that combines Retrieval-Augmented Generation (RAG), Redis caching, conversation memory, and LLM orchestration to answer banking policy questions, explain financial concepts, and perform financial calculations.

The project is designed using production-oriented AI engineering patterns rather than a simple chatbot architecture.

---

# Key Features

## Policy RAG

Answer banking-policy-related questions using source-grounded retrieval.

Examples:

* What is SBI's LTV ratio?
* Compare SBI and HDFC home loan policies.
* What are the foreclosure charges for HDFC loans?

---

## Hybrid Retrieval Pipeline

Instead of relying solely on vector search, FinWise uses:

* Semantic Vector Search
* BM25 Lexical Search
* Reciprocal Rank Fusion (RRF)
* Cross Encoder Reranking

This improves retrieval accuracy and relevance for banking documents.

---

## Financial Concept Explanations

Examples:

* What is SIP?
* What is inflation?
* What is compounding?
* What is an ETF?
* What is a debt fund?

---

## EMI Calculator

Perform EMI calculations directly from user-provided inputs.

Example:

> Calculate EMI for ₹60,000 at 17% interest for 12 months.

Outputs:

* Monthly EMI
* Total Payment
* Total Interest Paid

---

## Conversation Memory

FinWise maintains context using:

### Short-Term Memory

Recent conversation history.

### Long-Term Memory

Conversation summaries generated periodically.

---

## Redis Caching

### Summary Cache

Reduces PostgreSQL reads by storing conversation summaries in Redis.

### Response Cache

Avoids repeated LLM execution for identical requests.

---

## Async Background Processing

Conversation summaries are generated asynchronously after user responses are returned, improving response latency.

---

# System Architecture

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
 ├── EMI Calculator
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
Message Storage
 │
 ▼
Background Summary Generation
 │
 ▼
Redis Summary Cache
```

---

# Technology Stack

## Backend

* FastAPI
* Python 3.11+

## Database

* PostgreSQL
* AsyncPG

## Caching

* Redis

## LLM Layer

* Ollama
* Llama 3.2

## RAG Stack

* ChromaDB
* Sentence Transformers
* BM25
* Cross Encoder Reranker

## AI Frameworks

* LangChain

---

# Project Structure

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

# Local Setup

## Prerequisites

Install the following:

* Python 3.11+
* PostgreSQL
* Docker Desktop
* Ollama

Verify:

```bash
python --version
docker --version
ollama --version
```

---

## Clone Repository

```bash
git clone https://github.com/parthib01/finwise-ai.git

cd finwise-ai
```

---

## Create Virtual Environment

Windows:

```bash
python -m venv .venv

.venv\Scripts\activate
```

Linux / Mac:

```bash
python -m venv .venv

source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -e .
```

---

# PostgreSQL Setup

Create database:

```sql
CREATE DATABASE finwise_ai;
```

Update database connection settings according to your local PostgreSQL installation.

Current application expects:

```text
postgresql://postgres:<password>@localhost:5432/finwise_ai
```

---

# Redis Setup

Pull Redis image:

```bash
docker pull redis:7
```

Create Redis container:

```bash
docker run -d \
  --name finwise-redis \
  -p 6379:6379 \
  redis:7
```

Verify:

```bash
docker ps
```

Expected:

```text
CONTAINER ID   IMAGE     STATUS
xxxxxxxx       redis:7   Up ...
```

Test Redis:

```bash
docker exec -it finwise-redis redis-cli ping
```

Expected:

```text
PONG
```

For subsequent runs:

```bash
docker start finwise-redis
```

---

# Ollama Setup

Start Ollama:

```bash
ollama serve
```

Pull model:

```bash
ollama pull llama3.2:3b
```

Verify:

```bash
ollama list
```

---

# Run Application

```bash
uvicorn app.main:app --reload
```

Application:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

---

# Example Queries

## Policy Questions

* What is SBI home loan LTV ratio?
* Compare SBI and HDFC home loan policies.
* What are HDFC foreclosure charges?

## Financial Concepts

* What is SIP?
* What is inflation?
* What is compounding?
* What is ETF?

## EMI Calculations

* Calculate EMI for ₹5 lakh at 11% interest for 5 years.
* Calculate EMI for ₹60,000 at 17% interest for 12 months.

---

# Performance Optimizations

### Hybrid Retrieval

Combines lexical and semantic search.

### Reciprocal Rank Fusion

Improves recall by combining multiple retrievers.

### Cross Encoder Reranking

Improves final retrieval precision.

### Redis Summary Cache

Reduces database load.

### Redis Response Cache

Reduces LLM latency.

### Async Background Summarization

Improves user-facing response times.

---

# Current Release

```text
v0.1.0
```

Features included:

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

---

# Roadmap

## Next Milestones

* Retrieval Cache
* Dockerization
* Docker Compose
* Kubernetes Deployment
* CI/CD Pipelines
* Monitoring & Observability

---

# Author

**Parthib Banerjee**

Software Engineer focused on AI Engineering, Retrieval-Augmented Generation (RAG), LLM Systems, and Enterprise AI Applications.
