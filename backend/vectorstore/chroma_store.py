import chromadb
from openai import OpenAI
from config import CHROMA_DB_PATH, EMBED_MODEL, OPENAI_API_KEY, PDF_COLLECTION, EXCEL_COLLECTION, WEBSITE_COLLECTION

_openai_client = None
_chroma_client = None


def get_openai():
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def get_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _chroma_client


def get_collection(name: str):
    return get_client().get_or_create_collection(name=name)


def embed_text(text: str) -> list:
    response = get_openai().embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding


def embed_texts(texts: list) -> list:
    response = get_openai().embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in response.data]


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
