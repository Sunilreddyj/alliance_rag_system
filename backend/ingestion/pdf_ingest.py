import os
import uuid
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vectorstore.chroma_store import get_collection, embed_text
from config import PDF_COLLECTION, CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    doc = fitz.open(pdf_path)
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


def ingest_pdf(pdf_path: str, source_label: str = None) -> dict:
    filename = source_label or os.path.basename(pdf_path)
    raw_text = extract_text_from_pdf(pdf_path)

    if not raw_text.strip():
        return {"filename": filename, "status": "skipped", "reason": "No text found (scanned PDF)", "chunks": 0}

    chunks = chunk_text(raw_text)
    col = get_collection(PDF_COLLECTION)

    ids, docs, embeddings, metadatas = [], [], [], []
    for chunk in chunks:
        ids.append(str(uuid.uuid4()))
        docs.append(chunk)
        embeddings.append(embed_text(chunk))
        metadatas.append({"source": filename, "type": "pdf"})

    col.add(documents=docs, ids=ids, embeddings=embeddings, metadatas=metadatas)
    return {"filename": filename, "status": "indexed", "chunks": len(chunks)}


def delete_pdf_by_source(filename: str) -> int:
    col = get_collection(PDF_COLLECTION)
    results = col.get(where={"source": filename}, include=[])
    ids = results.get("ids", [])
    if ids:
        col.delete(ids=ids)
    return len(ids)


def list_indexed_pdfs() -> list:
    col = get_collection(PDF_COLLECTION)
    if col.count() == 0:
        return []
    results = col.get(include=["metadatas"])
    seen = set()
    files = []
    for meta in results.get("metadatas", []):
        src = meta.get("source", "")
        if src and src not in seen:
            seen.add(src)
            files.append(src)
    return sorted(files)
