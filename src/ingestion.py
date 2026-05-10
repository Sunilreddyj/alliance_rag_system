import os
import uuid
import requests
import fitz
from bs4 import BeautifulSoup
import chromadb

from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHROMA_DB_PATH, EMBED_MODEL

embed_model = SentenceTransformer(EMBED_MODEL)

chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

pdf_store = chroma_client.get_or_create_collection(name="alliance_pdf_rag")
website_store = chroma_client.get_or_create_collection(name="alliance_website_rag")
user_pdf_store = chroma_client.get_or_create_collection(name="user_uploaded_pdfs")


def embed_text(text):
    return embed_model.encode(text).tolist()


def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120
    )
    return splitter.split_text(text)


def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        page_text = page.get_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def store_local_pdf(pdf_path):
    # Skip if already indexed
    if pdf_store.count() > 0:
        return

    if not os.path.exists(pdf_path):
        return

    raw_text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(raw_text)

    for chunk in chunks:
        pdf_store.add(
            documents=[chunk],
            ids=[str(uuid.uuid4())],
            embeddings=[embed_text(chunk)],
            metadatas=[{"source": os.path.basename(pdf_path)}]
        )


def store_uploaded_pdfs(pdf_paths, clear_existing=False):
    """Process and index a list of uploaded PDF file paths."""
    if clear_existing:
        clear_user_pdfs()

    results = []
    for path in pdf_paths:
        try:
            filename = os.path.basename(path)
            raw_text = extract_text_from_pdf(path)
            if not raw_text.strip():
                results.append(f"⚠ {filename}: No text found (possibly scanned image PDF)")
                continue

            chunks = chunk_text(raw_text)

            for chunk in chunks:
                user_pdf_store.add(
                    documents=[chunk],
                    ids=[str(uuid.uuid4())],
                    embeddings=[embed_text(chunk)],
                    metadatas=[{"source": filename}]
                )
            results.append(f"✓ {filename}: {len(chunks)} chunks indexed")
        except Exception as e:
            results.append(f"✗ {os.path.basename(path)}: Error - {str(e)}")

    return results


def clear_user_pdfs():
    """Remove all user-uploaded PDF chunks by deleting their IDs."""
    ids = user_pdf_store.get(include=[])["ids"]
    if ids:
        user_pdf_store.delete(ids=ids)


def fetch_website_text(url):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator=" ").strip()


def index_website_pages(urls):
    # Skip if already indexed
    if website_store.count() > 0:
        return

    for url in urls:
        try:
            text = fetch_website_text(url)
            chunks = chunk_text(text)
            for chunk in chunks:
                website_store.add(
                    documents=[chunk],
                    ids=[str(uuid.uuid4())],
                    embeddings=[embed_text(chunk)],
                    metadatas=[{"source": url}]
                )
        except Exception:
            pass
