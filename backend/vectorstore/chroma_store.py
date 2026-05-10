import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_DB_PATH, EMBED_MODEL, PDF_COLLECTION, EXCEL_COLLECTION, WEBSITE_COLLECTION

_embed_model = None
_chroma_client = None


def get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBED_MODEL)
    return _embed_model


def get_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _chroma_client


def get_collection(name: str):
    return get_client().get_or_create_collection(name=name)


def embed_text(text: str) -> list:
    return get_embed_model().encode(text).tolist()


def embed_texts(texts: list) -> list:
    return get_embed_model().encode(texts).tolist()


def collection_stats() -> dict:
    client = get_client()
    stats = {}
    for name in [PDF_COLLECTION, EXCEL_COLLECTION, WEBSITE_COLLECTION]:
        try:
            col = client.get_or_create_collection(name=name)
            stats[name] = col.count()
        except Exception:
            stats[name] = 0
    return stats


def clear_collection(name: str):
    col = get_collection(name)
    ids = col.get(include=[])["ids"]
    if ids:
        col.delete(ids=ids)
    return len(ids)
