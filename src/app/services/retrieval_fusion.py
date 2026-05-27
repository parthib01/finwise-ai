from collections import defaultdict


def reciprocal_rank_fusion(
    vector_results,
    bm25_results,
    k=60
):
    """
    Combines:
    - Vector Retrieval Results
    - BM25 Retrieval Results

    using Reciprocal Rank Fusion (RRF).

    Formula:
        score += 1 / (k + rank)

    Higher-ranked documents get higher fused scores.

    This implementation also:
    - deduplicates chunks
    - preserves first-seen document object
    - accumulates scores across retrievers
    """

    # =========================================
    # FUSED SCORES
    # =========================================

    fused_scores = defaultdict(float)

    # =========================================
    # DOC STORAGE
    # =========================================

    doc_map = {}

    # =========================================
    # VECTOR RESULTS
    # =========================================

    for rank, (doc, score) in enumerate(vector_results):

        # Stable content-based ID
        doc_id = hash(
            doc.page_content.strip()
        )

        # RRF score accumulation
        fused_scores[doc_id] += 1 / (k + rank + 1)

        # Preserve first-seen doc
        if doc_id not in doc_map:

            doc_map[doc_id] = {
                "doc": doc,
                "source": "vector"
            }

    # =========================================
    # BM25 RESULTS
    # =========================================

    for rank, item in enumerate(bm25_results):

        # Stable content-based ID
        doc_id = hash(
            item["content"].strip()
        )

        # RRF score accumulation
        fused_scores[doc_id] += 1 / (k + rank + 1)

        # Preserve first-seen doc
        if doc_id not in doc_map:

            doc_map[doc_id] = {
                "doc": item,
                "source": "bm25"
            }

    # =========================================
    # SORT BY FUSED SCORE
    # =========================================

    ranked = sorted(
        fused_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # =========================================
    # FINAL RESULTS
    # =========================================

    final_results = []

    for doc_id, score in ranked:

        final_results.append({
            "score": score,
            "data": doc_map[doc_id]
        })

    return final_results