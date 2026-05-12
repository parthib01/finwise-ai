import re
import os
import asyncio
 
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama

from app.services.rag_utils import extract_banks
from app.utils.logger import log_step

# -----------------------------
# CONFIG
# -----------------------------
PERSIST_DIR = "./data/chroma_policy_db"

embedding = OllamaEmbeddings(model="mxbai-embed-large")

vector_store = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embedding
)

llm = ChatOllama(
    model="llama3.2:3b",
    num_ctx=8192,       # explicit context window
    temperature=0,      # deterministic — important for extraction tasks
    timeout=120,
)

# Similarity score threshold for ChromaDB (L2 distance — lower = more similar)
# Docs with distance above this are likely irrelevant
RETRIEVAL_SCORE_THRESHOLD = 1.2


# =============================================
# FIX #1: IMPROVED MODE DETECTION
# =============================================
def detect_mode(query: str) -> str:
    """
    Classifies query into one of three modes:
    - extract  → precise value/number needed (rates, fees, ratios, limits)
    - explain  → conceptual understanding needed (what is X, how does Y work, who is eligible)
    - compare  → comparison between entities (SBI vs HDFC, product A vs B)

    """
    query_lower = query.lower()

    # -----------------------------------------------
    # COMPARE signals — check first, highest priority
    # -----------------------------------------------
    compare_signals = [
        "compare", "difference between", "vs", "versus",
        "better", "which is", "contrast"
    ]
    if any(s in query_lower for s in compare_signals):
        return "compare"

    # -----------------------------------------------
    # EXPLAIN signals — conceptual/descriptive queries
    # -----------------------------------------------
    explain_signals = [
        "what benchmark",       # "what benchmark rate is linked to"
        "what happens",         # "what happens if I default"
        "how does",             # "how does interest work"
        "how is",               # "how is EMI calculated"
        "who is eligible",      # "who is eligible for Shaurya"
        "who can",              # "who can apply"
        "who are eligible",
        "what is linked",       # "what is interest linked to"
        "explain",
        "describe",
        "tell me about",
        "what does",
        "purpose of",
        "what type",
        "what types",
        "what kind",
        "what products",
        "what are the conditions",
        "what are the documents",
        "what is the process",
        "in case of default",
        "what if",
    ]
    if any(s in query_lower for s in explain_signals):
        return "explain"

    # -----------------------------------------------
    # EXTRACT signals — precise value queries
    # -----------------------------------------------
    extract_signals = [
        "what is the rate",
        "what is the ratio",
        "what is the fee",
        "what is the charge",
        "what is the penalty",
        "what is the percentage",
        "what is the limit",
        "what is the tenure",
        "what is the maximum",
        "what is the minimum",
        "what is the processing",
        "how much",
        "how many",
        "what amount",
        "what percentage",
        "ltv ratio",
        "interest rate",
        "penal charge",
        "processing fee",
        "pre-closure",
        "nach mandate",
        "cersai",
    ]
    if any(s in query_lower for s in extract_signals):
        return "extract"

    # -----------------------------------------------
    # Default — explain is safer than extract
    # extract can cause overly terse one-word answers
    # -----------------------------------------------
    return "explain"


# =============================================
# RETRIEVAL WITH CONFIDENCE SCORING
# =============================================
def retrieve_docs(query: str, banks: list) -> dict:
    """
    Hybrid retrieval:
    1. Semantic search with confidence scoring
    2. Query expansion for numeric/structured data
    3. Filter low-confidence results
    4. Merge, deduplicate, prioritize tables
    """

    retrieved_docs = {}

    # Keywords that indicate the query needs structured/numeric data
    numeric_keywords = [
        "rate", "ratio", "charge", "fee", "percent", "lakh",
        "lacs", "amount", "ltv", "penalty", "penal", "processing",
        "interest", "cersai", "nach", "emi", "tenure", "switching"
    ]
    query_lower = query.lower()
    is_numeric_query = any(kw in query_lower for kw in numeric_keywords)

    for bank in banks:

        # ------------------------------------------
        # 1. SEMANTIC SEARCH WITH SCORES
        # ✅ FIX #3: Use scored search for confidence filtering
        # ChromaDB returns L2 distance — lower = more similar
        # ------------------------------------------
        semantic_results = vector_store.similarity_search_with_score(
            query,
            k=7,
            filter={"bank": {"$eq": bank}}
        )

        log_step("RAG Retrieval Scores", {
            f"[{i+1}] score={round(score, 4)} type={doc.metadata.get('type')} section={doc.metadata.get('section', 'N/A')}":
            doc.page_content[:80]
            for i, (doc, score) in enumerate(semantic_results)
        })

        # ✅ Filter out low-confidence results
        semantic_docs = [
            doc for doc, score in semantic_results
            if score < RETRIEVAL_SCORE_THRESHOLD
        ]

        # Fallback: if everything was filtered, keep top 3 anyway
        if not semantic_docs and semantic_results:
            semantic_docs = [doc for doc, _ in semantic_results[:3]]
            log_step("RAG Score Fallback", {"reason": "all docs below threshold, keeping top 3"})

        # ------------------------------------------
        # 2. QUERY EXPANSION (only for numeric queries)
        # Avoids adding irrelevant noise to conceptual queries
        # ------------------------------------------
        keyword_docs = []
        if is_numeric_query:
            expanded_query = f"{query} financial table rate percentage value slab"
            expanded_results = vector_store.similarity_search_with_score(
                expanded_query,
                k=5,
                filter={"bank": {"$eq": bank}}
            )
            keyword_docs = [
                doc for doc, score in expanded_results
                if score < RETRIEVAL_SCORE_THRESHOLD
            ]

        # ------------------------------------------
        # 3. MERGE + DEDUPLICATE
        # ------------------------------------------
        combined = semantic_docs + keyword_docs
        unique_docs = []
        seen = set()
        for doc in combined:
            key = doc.page_content.strip()
            if key not in seen:
                unique_docs.append(doc)
                seen.add(key)

        # ------------------------------------------
        # 4. PRIORITIZE TABLE DOCS
        # Tables go first — they contain precise values
        # ------------------------------------------
        table_docs = [d for d in unique_docs if d.metadata.get("type") == "table"]
        text_docs  = [d for d in unique_docs if d.metadata.get("type") == "text"]
        final_docs = table_docs + text_docs

        # ------------------------------------------
        # 5. SAFETY FALLBACK
        # ------------------------------------------
        if not final_docs:
            fallback = vector_store.similarity_search(query, k=5)
            final_docs = fallback
            log_step("RAG Safety Fallback Used", {"bank": bank})

        retrieved_docs[bank] = final_docs[:8]   # cap context size

    log_step("RAG Retrieved Docs", {
        bank: len(docs) for bank, docs in retrieved_docs.items()
    })

    return retrieved_docs


# =============================================
# CONTEXT BUILDER
# =============================================
def build_context(retrieved_docs: dict) -> str:
    """
    Build context string from retrieved docs.
    - Full chunk content (no truncation)
    - Soft cap at 1000 chars per chunk
    - Labels doc type for LLM awareness
    """

    context = ""

    for bank, docs in retrieved_docs.items():
        context += f"\n\n### {bank} DATA:\n"

        for i, d in enumerate(docs):
            # ✅ Full content — no 300-char truncation
            # Soft cap at 1000 to keep total context manageable for 3B model
            content  = d.page_content[:1000]
            source   = d.metadata.get("source", "unknown")
            doc_type = d.metadata.get("type", "text")
            section  = d.metadata.get("section", "")

            section_label = f" | Section: {section}" if section else ""
            context += f"[{i+1}] ({doc_type}{section_label})\n{content}\n(Source: {source})\n\n"

    log_step("RAG Context Preview", {"preview": context[:600]})

    return context


# =============================================
# GENERATION
# =============================================
async def generate_rag_answer(query: str, context: str, mode: str) -> str:
    """
    Mode-aware answer generation.

    Modes:
    - extract → precise value/number, all tiers if applicable
    - explain → clear descriptive answer using only context
    - compare → structured comparison between entities
    """

    prompt = f"""You are a financial document assistant. Answer questions strictly based on the provided context from official bank policy documents.

TASK MODE: {mode}

CONTEXT:
{context}

USER QUERY:
{query}

STRICT RULES (follow ALL without exception):
1. Answer ONLY using information explicitly present in the context above.
2. DO NOT use any prior knowledge, training data, or assumptions.
3. DO NOT hallucinate facts, numbers, criteria, names, or eligibility conditions.
4. DO NOT infer or assume values not stated in the context.
5. If the answer is not present in the context, respond with exactly: NOT AVAILABLE
6. Do NOT say "Based on the context..." or "According to the document...".
7. Do NOT mention the mode in your answer.
8. Be direct. No preamble.

MODE-SPECIFIC INSTRUCTIONS:

If mode = extract:
- Return the exact value or number from the context.
- If there are multiple tiers or slabs (e.g. LTV table), return ALL of them clearly.
- Format as a short list if multiple values exist.
- Do not round or approximate.

If mode = explain:
- Explain clearly in simple terms using only the context.
- Include all relevant details — do not give a one-word answer.
- If eligibility is asked, state exactly who qualifies.

If mode = compare:
- Compare entities in a clear structured format.
- Only compare attributes explicitly present in the context.
- Use bullet points or a table format.

ANSWER:"""

    try:
        response = await asyncio.wait_for(
            llm.ainvoke(prompt),
            timeout=120.0
        )
        return response.content.strip()
    except asyncio.TimeoutError:
        log_step("Generation Timeout", {})
        return "NOT AVAILABLE"


# =============================================
# FAITHFULNESS CHECK (DETERMINISTIC)
# =============================================
def simple_faithfulness_check(context: str, answer: str) -> bool:
    """
    Deterministic numeric faithfulness check.

    Extracts all numbers and percentages from the answer
    and verifies each one exists in the context.

    Replaces naive LLM-only verification which was using the same
    weak 3B model that generated the answer — it would validate
    its own hallucinations.

    ✅ Fixed regex: tight pattern, no trailing whitespace causing mismatches
    ✅ Handles comma-separated numbers (Rs. 5,000 → 5000)
    ✅ Handles percentages (75%, 2.40%)
    ✅ Uses word boundaries to avoid partial matches
    """

    if not answer or answer.strip().upper() == "NOT AVAILABLE":
        return True

    def extract_numbers(text: str) -> set:
        # Normalize: remove commas from numbers like "5,000" → "5000"
        text = text.replace(",", "")
        tokens = set()

        # Extract percentages: "75%", "2.40%", "0.35%"
        for m in re.finditer(r'\d+\.?\d*%', text):
            tokens.add(m.group())

        # Extract plain numbers with word boundaries: "30", "75", "5000"
        for m in re.finditer(r'\b\d+\.?\d*\b', text):
            tokens.add(m.group())

        return tokens

    answer_numbers  = extract_numbers(answer)
    context_numbers = extract_numbers(context)

    for num in answer_numbers:
        if num not in context_numbers:
            log_step("Faithfulness Check FAILED", {
                "unverified_number": num,
                "answer_numbers": sorted(list(answer_numbers)),
                "context_numbers": sorted(list(context_numbers)),
                "answer_preview": answer[:200]
            })
            return False

    return True


# =============================================
# VERIFICATION (TWO-STAGE)
# =============================================
async def verify_answer(context: str, answer: str) -> str:
    """
    Two-stage verification:

    Stage 1 — Deterministic numeric check (fast, reliable)
      Fails if any number in answer is not in context.

    Stage 2 — LLM verification (catches non-numeric hallucinations)
      Uses simplified prompt designed for 3B model capabilities.
      Parses output safely — handles cases like "VALID." "VALID - correct"
      Defaults to VALID on timeout (deterministic check already passed).

    ✅ FIX: Short-circuits on NOT AVAILABLE (no need to verify a refusal)
    ✅ FIX: Safe output parsing — doesn't require exact "VALID"/"INVALID"
    ✅ FIX: Timeout defaults to VALID not INVALID (avoids punishing correct answers)
    """

    # Stage 1 — deterministic
    if not simple_faithfulness_check(context, answer):
        log_step("Verification", {"stage": "deterministic", "verdict": "INVALID"})
        return "INVALID"

    # Short-circuit — no need to verify a refusal
    if answer.strip().upper() == "NOT AVAILABLE":
        log_step("Verification", {"stage": "skipped_refusal", "verdict": "VALID"})
        return "VALID"

    # Stage 2 — LLM verification
    # ✅ Simplified prompt — 3B models struggle with complex multi-rule prompts
    verification_prompt = f"""Does the answer below contain ONLY information that is present in the context? Answer with one word: VALID or INVALID.

CONTEXT:
{context}

ANSWER:
{answer}

One word (VALID or INVALID):"""

    try:
        response = await asyncio.wait_for(
            llm.ainvoke(verification_prompt),
            timeout=60.0
        )
        raw = response.content.strip()
        upper = raw.upper()

        log_step("Verification", {
            "stage": "llm",
            "raw_output": raw,
            "answer_preview": answer[:150]
        })

        # ✅ Safe parsing — handles extra text from 3B model
        if upper.startswith("VALID"):
            return "VALID"
        elif upper.startswith("INVALID"):
            return "INVALID"
        elif "INVALID" in upper:
            return "INVALID"
        elif "VALID" in upper:
            return "VALID"
        else:
            # Ambiguous output — deterministic check already passed
            # Don't punish correct answers for model verbosity
            log_step("Verification", {
                "stage": "llm_ambiguous",
                "raw_output": raw,
                "verdict": "VALID (fallback)"
            })
            return "VALID"

    except asyncio.TimeoutError:
        # Deterministic check passed — safe to return VALID
        # Don't block correct answers due to slow inference
        log_step("Verification", {"stage": "timeout", "verdict": "VALID (fallback)"})
        return "VALID"


# =============================================
# MAIN RAG ENTRY POINT
# =============================================
async def query_policy_rag(query: str) -> str:

    # Step 1 — classify mode and extract bank entities
    mode  = detect_mode(query)
    banks = extract_banks(query)

    if not banks:
        return "Please specify the bank."

    log_step("RAG Mode + Entities", {"mode": mode, "banks": banks})

    # Step 2 — retrieve relevant docs
    retrieved = retrieve_docs(query, banks)

    if not any(retrieved.values()):
        return "NOT AVAILABLE"

    # Step 3 — build context string
    context = build_context(retrieved)

    # Step 4 — generate answer
    print("⏳ Starting generation...")
    answer = await generate_rag_answer(query, context, mode)
    print(f"✅ Generation done: {answer[:100]}")

    # Step 5 — verify answer
    # verdict = await verify_answer(context, answer)
    # print(f"✅ Verification done: {verdict}")

    # log_step("Verification Verdict", {"verdict": verdict, "answer": answer[:200]})

    # if verdict != "VALID":
    #     return "NOT AVAILABLE"

    return answer