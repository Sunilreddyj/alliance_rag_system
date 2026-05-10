import uuid
import io
import requests
import fitz
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vectorstore.chroma_store import get_collection, embed_text
from config import WEBSITE_COLLECTION, CHUNK_SIZE, CHUNK_OVERLAP


def fetch_website_text(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; RAGBot/1.0)"}
    response = requests.get(url, timeout=15, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def find_pdf_links(url: str) -> list:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; RAGBot/1.0)"}
    try:
        response = requests.get(url, timeout=15, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        pdf_links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.lower().endswith(".pdf"):
                full_url = urljoin(url, href)
                pdf_links.append(full_url)
        return list(set(pdf_links))
    except Exception:
        return []


def download_and_extract_pdf(pdf_url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; RAGBot/1.0)"}
    response = requests.get(pdf_url, timeout=20, headers=headers)
    response.raise_for_status()
    doc = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
    text = ""
    for page in doc:
        page_text = page.get_text()
        if page_text:
            text += page_text + "\n"
    doc.close()
    return text.strip()


def chunk_text(text: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)


def ingest_website(url: str, include_pdfs: bool = True) -> dict:
    col = get_collection(WEBSITE_COLLECTION)
    results = {"url": url, "page_chunks": 0, "pdf_chunks": 0, "pdf_links": [], "status": "ok"}

    # Scrape main page
    try:
        text = fetch_website_text(url)
        if text.strip():
            chunks = chunk_text(text)
            ids, docs, embeddings, metadatas = [], [], [], []
            for chunk in chunks:
                ids.append(str(uuid.uuid4()))
                docs.append(chunk)
                embeddings.append(embed_text(chunk))
                metadatas.append({"source": url, "type": "website"})
            col.add(documents=docs, ids=ids, embeddings=embeddings, metadatas=metadatas)
            results["page_chunks"] = len(chunks)
    except Exception as e:
        results["page_error"] = str(e)

    # Detect and process linked PDFs
    if include_pdfs:
        pdf_links = find_pdf_links(url)
        results["pdf_links"] = pdf_links
        for pdf_url in pdf_links[:5]:  # cap at 5 PDFs per site
            try:
                pdf_text = download_and_extract_pdf(pdf_url)
                if pdf_text.strip():
                    chunks = chunk_text(pdf_text)
                    ids, docs, embeddings, metadatas = [], [], [], []
                    for chunk in chunks:
                        ids.append(str(uuid.uuid4()))
                        docs.append(chunk)
                        embeddings.append(embed_text(chunk))
                        metadatas.append({"source": pdf_url, "type": "website_pdf"})
                    col.add(documents=docs, ids=ids, embeddings=embeddings, metadatas=metadatas)
                    results["pdf_chunks"] += len(chunks)
            except Exception:
                pass

    return results


def delete_website_by_url(url: str) -> int:
    col = get_collection(WEBSITE_COLLECTION)
    results = col.get(where={"source": url}, include=[])
    ids = results.get("ids", [])
    if ids:
        col.delete(ids=ids)
    return len(ids)


def list_indexed_websites() -> list:
    col = get_collection(WEBSITE_COLLECTION)
    if col.count() == 0:
        return []
    results = col.get(include=["metadatas"])
    seen = set()
    sites = []
    for meta in results.get("metadatas", []):
        src = meta.get("source", "")
        if src and src not in seen:
            seen.add(src)
            sites.append({"url": src, "type": meta.get("type", "website")})
    return sites
