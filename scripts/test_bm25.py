from app.services.bm25_service import bm25_search

query = "Compare SBI vs HDFC interest rates"

results = bm25_search(query)

print("\nBM25 RESULTS:\n")

for r in results:

    print("--------------------------------------------------")
    print("SCORE:", r["score"])
    print("BANK:", r["metadata"].get("bank"))
    print("TYPE:", r["metadata"].get("type"))
    print(r["content"][:500])