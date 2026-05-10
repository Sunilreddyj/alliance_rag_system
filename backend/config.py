import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "alliance-rag-secret-key-change-me")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "alliance2024")
ALLOWED_EMAILS = [e.strip() for e in os.getenv("ALLOWED_EMAILS", "").split(",") if e.strip()]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def _resolve_dir(env_key, default):
    path = os.getenv(env_key, default)
    try:
        os.makedirs(path, exist_ok=True)
        return path
    except PermissionError:
        # Env var points somewhere we can't write (e.g. /data without a disk)
        # Fall back to a path inside the project directory
        fallback = os.path.join(BASE_DIR, os.path.basename(path))
        os.makedirs(fallback, exist_ok=True)
        return fallback

CHROMA_DB_PATH = _resolve_dir("CHROMA_DB_PATH", os.path.join(BASE_DIR, "chroma_multi_store"))
UPLOAD_DIR     = _resolve_dir("UPLOAD_DIR",      os.path.join(BASE_DIR, "uploads"))

EMBED_MODEL = "mixedbread-ai/mxbai-embed-large-v1"
LLM_MODEL = "gpt-4o-mini"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 120

# Collection names
PDF_COLLECTION = "pdf_documents"
EXCEL_COLLECTION = "excel_documents"
WEBSITE_COLLECTION = "website_documents"
