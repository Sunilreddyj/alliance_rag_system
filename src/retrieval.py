from ingestion import pdf_store, website_store, embed_text


def search_pdf(query):

    res = pdf_store.query(
        query_embeddings=[embed_text(query)],
        n_results=3
    )

    return res.get("documents", [[]])[0]


def search_website(query):

    res = website_store.query(
        query_embeddings=[embed_text(query)],
        n_results=3
    )

    return res.get("documents", [[]])[0]