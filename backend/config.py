import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "alliance-rag-secret-key-change-me")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "alliance2024")
ALLOWED_EMAILS = [e.strip() for e in os.getenv("ALLOWED_EMAILS", "").split(",") if e.strip()]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# On Render, CHROMA_DB_PATH / UPLOAD_DIR are overridden via env vars
# so data lands on the mounted persistent disk (/data/...)
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", os.path.join(BASE_DIR, "chroma_multi_store"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

EMBED_MODEL = "mixedbread-ai/mxbai-embed-large-v1"
LLM_MODEL = "gpt-4o-mini"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 120

# Collection names
PDF_COLLECTION = "pdf_documents"
EXCEL_COLLECTION = "excel_documents"
WEBSITE_COLLECTION = "website_documents"
