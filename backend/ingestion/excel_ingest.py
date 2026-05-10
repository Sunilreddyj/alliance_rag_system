import os
import uuid
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vectorstore.chroma_store import get_collection, embed_text
from config import EXCEL_COLLECTION, CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_from_excel(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df_map = {"Sheet1": pd.read_csv(file_path)}
    else:
        df_map = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")

    parts = []
    for sheet_name, df in df_map.items():
        df = df.dropna(how="all").fillna("")
        parts.append(f"=== Sheet: {sheet_name} ===")
        # Add column headers as context
        headers = " | ".join(str(c) for c in df.columns)
        parts.append(f"Columns: {headers}")
        for _, row in df.iterrows():
            row_text = " | ".join(f"{col}: {val}" for col, val in row.items() if str(val).strip())
            if row_text.strip():
                parts.append(row_text)

    return "\n".join(parts)


def chunk_text(text: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)


def ingest_excel(file_path: str, source_label: str = None) -> dict:
    filename = source_label or os.path.basename(file_path)
    try:
        raw_text = extract_text_from_excel(file_path)
    except Exception as e:
        return {"filename": filename, "status": "error", "reason": str(e), "chunks": 0}

    if not raw_text.strip():
        return {"filename": filename, "status": "skipped", "reason": "Empty file", "chunks": 0}

    chunks = chunk_text(raw_text)
    col = get_collection(EXCEL_COLLECTION)

    ids, docs, embeddings, metadatas = [], [], [], []
    for chunk in chunks:
        ids.append(str(uuid.uuid4()))
        docs.append(chunk)
        embeddings.append(embed_text(chunk))
        metadatas.append({"source": filename, "type": "excel"})

    col.add(documents=docs, ids=ids, embeddings=embeddings, metadatas=metadatas)
    return {"filename": filename, "status": "indexed", "chunks": len(chunks)}


def delete_excel_by_source(filename: str) -> int:
    col = get_collection(EXCEL_COLLECTION)
    results = col.get(where={"source": filename}, include=[])
    ids = results.get("ids", [])
    if ids:
        col.delete(ids=ids)
    return len(ids)


def list_indexed_excels() -> list:
    col = get_collection(EXCEL_COLLECTION)
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
