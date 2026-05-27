from rank_bm25 import BM25Okapi

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


# =========================================
# CONFIG
# =========================================

PERSIST_DIR = "./data/chroma_policy_db"

embedding = OllamaEmbeddings(
    model="mxbai-embed-large"
)

vector_store = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embedding
)

# =========================================
# SINGLETON CACHE
# =========================================

_bm25 = None
_documents = None
_metadatas = None


# =========================================
# INITIALIZATION
# =========================================

def initialize_bm25():

    global _bm25
    global _documents
    global _metadatas

    # already initialized
    if _bm25 is not None:
        return

    # -------------------------------------
    # LOAD CHUNKS
    # -------------------------------------

    all_docs = vector_store.get()

    _documents = all_docs["documents"]
    _metadatas = all_docs["metadatas"]

    # -------------------------------------
    # TOKENIZATION
    # -------------------------------------

    tokenized_docs = [
        doc.lower().split()
        for doc in _documents
    ]

    # -------------------------------------
    # BM25 INDEX
    # -------------------------------------

    _bm25 = BM25Okapi(tokenized_docs)

    print(
        f"\n✅ BM25 index initialized with "
        f"{len(_documents)} chunks"
    )


# =========================================
# SEARCH
# =========================================

def bm25_search(query: str, top_k: int = 5):

    initialize_bm25()

    tokenized_query = query.lower().split()

    scores = _bm25.get_scores(tokenized_query)

    ranked = sorted(
        enumerate(scores),
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    for idx, score in ranked[:top_k]:

        results.append({
            "content": _documents[idx],
            "metadata": _metadatas[idx],
            "score": score
        })

    return results