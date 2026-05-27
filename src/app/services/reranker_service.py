from sentence_transformers import CrossEncoder


# =========================================
# MODEL CACHE
# =========================================

_reranker = None


# =========================================
# INITIALIZATION
# =========================================

def get_reranker():

    global _reranker

    if _reranker is None:

        print("\n🚀 Loading reranker model...")

        _reranker = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

        print("✅ Reranker loaded")

    return _reranker


# =========================================
# RERANK FUNCTION
# =========================================

def rerank_documents(query, docs, top_k=5):

    reranker = get_reranker()

    # -------------------------------------
    # CREATE QUERY-DOC PAIRS
    # -------------------------------------

    pairs = [
        (query, doc.page_content)
        for doc in docs
    ]

    # -------------------------------------
    # GET RELEVANCE SCORES
    # -------------------------------------

    scores = reranker.predict(pairs)

    # -------------------------------------
    # SORT DOCS
    # -------------------------------------

    ranked = sorted(
        zip(docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    # -------------------------------------
    # FINAL DOCS
    # -------------------------------------

    final_docs = []

    for doc, score in ranked[:top_k]:

        doc.metadata["rerank_score"] = float(score)

        final_docs.append(doc)

    return final_docs