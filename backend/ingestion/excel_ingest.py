import os
import uuid
import pandas as pd
from vectorstore.chroma_store import get_collection, embed_text
from config import EXCEL_COLLECTION


def _row_to_text(row: dict) -> str:
    """Convert a row dict to a rich searchable text string."""
    parts = []
    for col, val in row.items():
        val = str(val).strip()
        if val and val.lower() not in ("nan", "none", ""):
            parts.append(f"{col}: {val}")
    return "\n".join(parts)


def extract_rows_from_excel(file_path: str) -> list[dict]:
    """Return a list of row dicts from any Excel/CSV file."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df_map = {"Sheet1": pd.read_csv(file_path)}
    elif ext == ".xls":
        df_map = pd.read_excel(file_path, sheet_name=None, engine="xlrd")
    else:
        df_map = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")

    rows = []
    for sheet_name, df in df_map.items():
        df = df.dropna(how="all").fillna("")
        for _, row in df.iterrows():
            row_dict = {str(col): str(val) for col, val in row.items()}
            row_dict["__sheet__"] = sheet_name
            rows.append(row_dict)
    return rows


def ingest_excel(file_path: str, source_label: str = None) -> dict:
    filename = source_label or os.path.basename(file_path)
    try:
        rows = extract_rows_from_excel(file_path)
    except Exception as e:
        return {"filename": filename, "status": "error", "reason": str(e), "chunks": 0}

    if not rows:
        return {"filename": filename, "status": "skipped", "reason": "Empty file", "chunks": 0}

    col = get_collection(EXCEL_COLLECTION)
    ids, docs, embeddings, metadatas = [], [], [], []

    for row in rows:
        text = _row_to_text({k: v for k, v in row.items() if k != "__sheet__"})
        if not text.strip():
            continue
        ids.append(str(uuid.uuid4()))
        docs.append(text)
        embeddings.append(embed_text(text))
        metadatas.append({
            "source": filename,
            "sheet": row.get("__sheet__", ""),
            "type": "excel",
        })

    if not ids:
        return {"filename": filename, "status": "skipped", "reason": "No non-empty rows", "chunks": 0}

    col.add(documents=docs, ids=ids, embeddings=embeddings, metadatas=metadatas)
    return {"filename": filename, "status": "indexed", "chunks": len(ids)}


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
