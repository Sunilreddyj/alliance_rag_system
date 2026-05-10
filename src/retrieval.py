from ingestion import pdf_store, website_store, user_pdf_store, embed_text


def _safe_query(collection, query, n_results=5):
    try:
        count = collection.count()
        if count == 0:
            return []
        actual_n = min(n_results, count)
        res = collection.query(
            query_embeddings=[embed_text(query)],
            n_results=actual_n,
            include=["documents", "metadatas"]
        )
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        return list(zip(docs, metas))
    except Exception:
        return []


def search_pdf(query, n_results=5):
    return _safe_query(pdf_store, query, n_results)


def search_website(query, n_results=5):
    return _safe_query(website_store, query, n_results)


def search_user_pdfs(query, n_results=5):
    return _safe_query(user_pdf_store, query, n_results)


def search_all(query, n_results=5):
    """Search across all collections and return combined context."""
    all_results = []

    pdf_results = search_pdf(query, n_results)
    for doc, meta in pdf_results:
        all_results.append({"text": doc, "source": meta.get("source", "Alliance PDF")})

    user_results = search_user_pdfs(query, n_results)
    for doc, meta in user_results:
        all_results.append({"text": doc, "source": meta.get("source", "Uploaded PDF")})

    website_results = search_website(query, n_results)
    for doc, meta in website_results:
        all_results.append({"text": doc, "source": meta.get("source", "Website")})

    return all_results
