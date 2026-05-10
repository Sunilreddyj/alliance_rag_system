from vectorstore.chroma_store import get_collection, embed_text
from config import WEBSITE_COLLECTION


def search(query: str, n_results: int = 5) -> list:
    col = get_collection(WEBSITE_COLLECTION)
    count = col.count()
    if count == 0:
        return []
    actual_n = min(n_results, count)
    res = col.query(
        query_embeddings=[embed_text(query)],
        n_results=actual_n,
        include=["documents", "metadatas", "distances"]
    )
    results = []
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    distances = res.get("distances", [[]])[0]
    for doc, meta, dist in zip(docs, metas, distances):
        results.append({
            "text": doc,
            "source": meta.get("source", "Website"),
            "type": meta.get("type", "website"),
            "score": round(1 - dist, 4),
        })
    return results
