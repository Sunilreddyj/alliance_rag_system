import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

CHROMA_DB_PATH = "chroma_multi_store"
EMBED_MODEL = "mixedbread-ai/mxbai-embed-large-v1"
LLM_MODEL = "gpt-4o-mini"