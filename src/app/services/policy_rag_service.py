import re
import asyncio

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.documents import Document

from app.services.rag_utils import extract_banks
from app.utils.logger import log_step

from app.services.bm25_service import bm25_search
from app.services.retrieval_fusion import reciprocal_rank_fusion
from app.services.reranker_service import rerank_documents


# =============================================
# CONFIG
# =============================================

PERSIST_DIR = "./data/chroma_policy_db"

embedding = OllamaEmbeddings(
    model="mxbai-embed-large"
)

vector_store = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embedding
)

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
    num_ctx=8192,
    timeout=120,
)


# =============================================
# MODE DETECTION
# =============================================

def detect_mode(query: str) -> str:

    query_lower = query.lower()

    compare_signals = [
        "compare",
        "vs",
        "versus",
        "difference",
        "better"
    ]

    if any(s in query_lower for s in compare_signals):
        return "compare"

    extract_signals = [
        "ratio",
        "rate",
        "percentage",
        "ltv",
        "charges",
        "fee",
        "penal",
        "amount",
        "processing fee",
        "interest rate",
        "repo",
        "linked",
        "what is the"
    ]

    if any(s in query_lower for s in extract_signals):
        return "extract"

    return "explain"


# =============================================
# HYBRID RETRIEVAL
# =============================================

def retrieve_docs(query: str, banks: list, mode: str):

    retrieved_docs = {}

    for bank in banks:

        # =====================================
        # VECTOR RETRIEVAL
        # =====================================

        vector_results = vector_store.similarity_search_with_score(
            query,
            k=7,
            filter={
                "bank": bank
            }
        )

        log_step(
            f"{bank} Vector Retrieval",
            {
                f"[{i+1}] score={round(score, 4)}":
                    doc.page_content[:100]

                for i, (doc, score)
                in enumerate(vector_results)
            }
        )

        # =====================================
        # BM25 RETRIEVAL
        # =====================================

        bm25_results = bm25_search(
            query,
            top_k=7
        )

        bm25_results = [
            r for r in bm25_results
            if r["metadata"].get("bank") == bank
        ]

        log_step(
            f"{bank} BM25 Retrieval",
            {
                f"[{i+1}] score={round(r['score'], 4)}":
                    r["content"][:100]

                for i, r
                in enumerate(bm25_results)
            }
        )

        # =====================================
        # RRF FUSION
        # =====================================

        fused = reciprocal_rank_fusion(
            vector_results,
            bm25_results
        )

        log_step(
            f"{bank} RRF Fusion",
            {
                f"[{i+1}] fused_score={round(item['score'], 4)}":
                (
                    item["data"]["doc"].page_content[:100]
                    if item["data"]["source"] == "vector"
                    else item["data"]["doc"]["content"][:100]
                )

                for i, item
                in enumerate(fused[:7])
            }
        )

        # =====================================
        # CONVERT TO DOCUMENTS
        # =====================================

        docs = []

        for item in fused[:7]:

            data = item["data"]

            # VECTOR DOC
            if data["source"] == "vector":

                docs.append(data["doc"])

            # BM25 DOC
            else:

                docs.append(
                    Document(
                        page_content=data["doc"]["content"],
                        metadata=data["doc"]["metadata"]
                    )
                )

        # =====================================
        # DEDUPLICATION
        # =====================================

        unique_docs = []

        seen = set()

        for doc in docs:

            key = hash(
                doc.page_content.strip()
            )

            if key not in seen:

                unique_docs.append(doc)

                seen.add(key)

        # =====================================
        # TABLE PRIORITIZATION
        # =====================================

        table_docs = [
            d for d in unique_docs
            if d.metadata.get("type") == "table"
        ]

        text_docs = [
            d for d in unique_docs
            if d.metadata.get("type") == "text"
        ]

        final_docs = table_docs + text_docs

        # =====================================
        # RERANKING
        # =====================================

        final_docs = rerank_documents(
            query=query,
            docs=final_docs,
            top_k=5
        )

        log_step(
            f"{bank} Reranked Docs",
            {
                f"[{i+1}] rerank_score={round(doc.metadata.get('rerank_score', 0), 4)}":
                    doc.page_content[:120]

                for i, doc
                in enumerate(final_docs)
            }
        )

        # =====================================
        # SAFETY FALLBACK
        # =====================================

        if not final_docs:

            fallback = vector_store.similarity_search(
                query,
                k=5,
                filter={
                    "bank": bank
                }
            )

            final_docs = fallback

            log_step(
                "RAG Safety Fallback Used",
                {
                    "bank": bank
                }
            )

        retrieved_docs[bank] = final_docs

    # =====================================
    # FINAL LOGGING
    # =====================================

    log_step(
        "RAG Retrieved Docs",
        {
            bank: len(docs)
            for bank, docs
            in retrieved_docs.items()
        }
    )

    return retrieved_docs


# =============================================
# MULTI-BANK CONTEXT
# =============================================

def build_context(retrieved_docs: dict):

    context = ""

    for bank, docs in retrieved_docs.items():

        context += (
            f"\n\n"
            f"================ BANK: {bank} ================\n"
        )

        for i, d in enumerate(docs):

            content = d.page_content[:1000]

            source = d.metadata.get(
                "source",
                "unknown"
            )

            doc_type = d.metadata.get(
                "type",
                "text"
            )

            section = d.metadata.get(
                "section",
                ""
            )

            section_label = (
                f" | Section: {section}"
                if section else ""
            )

            rerank_score = d.metadata.get(
                "rerank_score",
                None
            )

            rerank_text = (
                f" | rerank={round(rerank_score, 4)}"
                if rerank_score is not None
                else ""
            )

            context += (
                f"[{i+1}] "
                f"({doc_type}"
                f"{section_label}"
                f"{rerank_text})\n"
                f"{content}\n"
                f"(Source: {source})\n\n"
            )

    log_step(
        "RAG Context Preview",
        {
            "preview": context[:700]
        }
    )

    return context


# =============================================
# SINGLE BANK CONTEXT
# =============================================

def build_single_bank_context(
    bank: str,
    docs: list
):

    context = (
        f"\n\n"
        f"================ BANK: {bank} ================\n"
    )

    for i, d in enumerate(docs):

        content = d.page_content[:1000]

        source = d.metadata.get(
            "source",
            "unknown"
        )

        doc_type = d.metadata.get(
            "type",
            "text"
        )

        section = d.metadata.get(
            "section",
            ""
        )

        section_label = (
            f" | Section: {section}"
            if section else ""
        )

        rerank_score = d.metadata.get(
            "rerank_score",
            None
        )

        rerank_text = (
            f" | rerank={round(rerank_score, 4)}"
            if rerank_score is not None
            else ""
        )

        context += (
            f"[{i+1}] "
            f"({doc_type}"
            f"{section_label}"
            f"{rerank_text})\n"
            f"{content}\n"
            f"(Source: {source})\n\n"
        )

    return context


# =============================================
# GENERATION
# =============================================

async def generate_rag_answer(
    query: str,
    context: str,
    mode: str
):

    prompt = f"""
You are a financial document assistant.

TASK MODE:
{mode}

STRICT RULES:
1. Use ONLY the provided context
2. DO NOT hallucinate
3. DO NOT infer values
4. DO NOT mix information
5. If answer missing → return NOT AVAILABLE
6. Keep answer concise
7. Preserve percentages and numbers exactly

CONTEXT:
{context}

USER QUERY:
{query}

MODE INSTRUCTIONS:

IF MODE = extract:
- Return exact values only
- Return slab/range if present

IF MODE = explain:
- Explain using only context

IF MODE = compare:
- Compare carefully
- Keep banks separate

FINAL ANSWER:
"""

    try:

        response = await asyncio.wait_for(
            llm.ainvoke(prompt),
            timeout=120
        )

        return response.content.strip()

    except asyncio.TimeoutError:

        log_step(
            "Generation Timeout",
            {}
        )

        return "NOT AVAILABLE"


# =============================================
# BANK-SPECIFIC GENERATION
# =============================================

async def generate_bank_specific_answer(
    query: str,
    bank: str,
    docs: list,
    mode: str
):

    context = build_single_bank_context(
        bank,
        docs
    )

    answer = await generate_rag_answer(
        query=query,
        context=context,
        mode=mode
    )

    return {
        "bank": bank,
        "answer": answer,
        "context": context
    }


# =============================================
# VALIDATION
# =============================================

def simple_faithfulness_check(
    context: str,
    answer: str
):

    if (
        not answer or
        answer.strip().upper() == "NOT AVAILABLE"
    ):
        return True

    def extract_numbers(text):

        text = text.replace(",", "")

        tokens = set()

        for m in re.finditer(
            r'\d+\.?\d*%',
            text
        ):
            tokens.add(m.group())

        for m in re.finditer(
            r'\b\d+\.?\d*\b',
            text
        ):
            tokens.add(m.group())

        return tokens

    answer_numbers = extract_numbers(answer)

    context_numbers = extract_numbers(context)

    for num in answer_numbers:

        if num not in context_numbers:

            log_step(
                "Faithfulness Check FAILED",
                {
                    "unverified_number": num
                }
            )

            return False

    return True


# =============================================
# MAIN ENTRY
# =============================================

async def query_policy_rag(query: str):

    # =====================================
    # MODE + BANK EXTRACTION
    # =====================================

    mode = detect_mode(query)

    banks = extract_banks(query)

    if not banks:

        banks = ["SBI", "HDFC"]

    log_step(
        "RAG Mode + Entities",
        {
            "mode": mode,
            "banks": banks
        }
    )

    # =====================================
    # RETRIEVAL
    # =====================================

    retrieved = retrieve_docs(
        query,
        banks,
        mode
    )

    if not any(retrieved.values()):

        return "NOT AVAILABLE"

    # =====================================
    # ISOLATED BANK GENERATION
    # =====================================

    bank_answers = []

    for bank, docs in retrieved.items():

        print(
            f"\n⏳ Generating isolated answer for {bank}..."
        )

        result = await generate_bank_specific_answer(
            query=query,
            bank=bank,
            docs=docs,
            mode=mode
        )

        print(
            f"✅ {bank} generation done: "
            f"{result['answer'][:120]}"
        )

        bank_answers.append(result)

    # =====================================
    # SINGLE BANK RESPONSE
    # =====================================

    if len(bank_answers) == 1:

        final_answer = bank_answers[0]["answer"]

        log_step(
            "RAG Response Generated",
            {
                "response": final_answer
            }
        )

        return final_answer

    # =====================================
    # COMPARISON SYNTHESIS
    # =====================================

    comparison_prompt = f"""
You are a financial comparison assistant.

STRICT RULES:
- Use ONLY the provided bank answers
- DO NOT invent values
- DO NOT merge bank values
- DO NOT infer missing values
- Keep each bank isolated
- If info missing → say NOT AVAILABLE

USER QUERY:
{query}

BANK ANSWERS:
"""

    for item in bank_answers:

        comparison_prompt += f"""

BANK: {item['bank']}

ANSWER:
{item['answer']}
"""

    comparison_prompt += """

Generate a clean comparison answer.
"""

    print("\n⏳ Starting comparison synthesis...")

    response = await llm.ainvoke(
        comparison_prompt
    )

    final_answer = response.content.strip()

    print(
        f"✅ Comparison synthesis done: "
        f"{final_answer[:150]}"
    )

    log_step(
        "RAG Response Generated",
        {
            "response": final_answer
        }
    )

    return final_answer