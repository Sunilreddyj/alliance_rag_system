import os
import sys

# Make backend/ importable as root
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import shutil

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

from auth import authenticate_admin, verify_token
from agents.orchestrator import run_query
from ingestion.pdf_ingest import ingest_pdf, delete_pdf_by_source, list_indexed_pdfs
from ingestion.excel_ingest import ingest_excel, delete_excel_by_source, list_indexed_excels
from ingestion.website_ingest import ingest_website, delete_website_by_url, list_indexed_websites
from vectorstore.chroma_store import collection_stats, clear_collection
from config import UPLOAD_DIR, PDF_COLLECTION, EXCEL_COLLECTION, WEBSITE_COLLECTION

app = FastAPI(title="Alliance Fees & Policy Chatbot API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static HTML files
@app.get("/", include_in_schema=False)
def serve_chat():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/admin", include_in_schema=False)
def serve_admin():
    return FileResponse(os.path.join(STATIC_DIR, "admin.html"))


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    password: str


@app.post("/api/admin/login")
def admin_login(body: LoginRequest):
    token = authenticate_admin(body.password)
    return {"token": token, "role": "admin"}


# ── Query ─────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str


@app.post("/api/query")
def query_endpoint(body: QueryRequest):
    q = body.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        result = run_query(q)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── PDF Upload ────────────────────────────────────────────────────────────────

@app.post("/api/admin/upload-pdf")
def upload_pdf(
    file: UploadFile = File(...),
    _admin=Depends(verify_token),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    dest = os.path.join(UPLOAD_DIR, file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = ingest_pdf(dest, source_label=file.filename)
    return result


@app.delete("/api/admin/pdf/{filename}")
def delete_pdf(filename: str, _admin=Depends(verify_token)):
    removed = delete_pdf_by_source(filename)
    return {"filename": filename, "chunks_removed": removed}


@app.get("/api/admin/pdfs")
def list_pdfs(_admin=Depends(verify_token)):
    return {"files": list_indexed_pdfs()}


# ── Excel Upload ──────────────────────────────────────────────────────────────

@app.post("/api/admin/upload-excel")
def upload_excel(
    file: UploadFile = File(...),
    _admin=Depends(verify_token),
):
    allowed = (".xlsx", ".xls", ".csv")
    if not any(file.filename.lower().endswith(ext) for ext in allowed):
        raise HTTPException(status_code=400, detail="Only Excel/CSV files are accepted")

    dest = os.path.join(UPLOAD_DIR, file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = ingest_excel(dest, source_label=file.filename)
    return result


@app.delete("/api/admin/excel/{filename}")
def delete_excel(filename: str, _admin=Depends(verify_token)):
    removed = delete_excel_by_source(filename)
    return {"filename": filename, "chunks_removed": removed}


@app.get("/api/admin/excels")
def list_excels(_admin=Depends(verify_token)):
    return {"files": list_indexed_excels()}


# ── Website Indexing ──────────────────────────────────────────────────────────

class WebsiteRequest(BaseModel):
    url: str
    include_pdfs: Optional[bool] = True


@app.post("/api/admin/index-website")
def index_website(body: WebsiteRequest, _admin=Depends(verify_token)):
    if not body.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL")
    try:
        result = ingest_website(body.url, include_pdfs=body.include_pdfs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/admin/website")
def delete_website(url: str, _admin=Depends(verify_token)):
    removed = delete_website_by_url(url)
    return {"url": url, "chunks_removed": removed}


@app.get("/api/admin/websites")
def list_websites(_admin=Depends(verify_token)):
    return {"sites": list_indexed_websites()}


# ── Stats ─────────────────────────────────────────────────────────────────────

@app.get("/api/admin/stats")
def get_stats(_admin=Depends(verify_token)):
    return collection_stats()


@app.delete("/api/admin/clear/{collection}")
def clear_col(collection: str, _admin=Depends(verify_token)):
    valid = {
        "pdf": PDF_COLLECTION,
        "excel": EXCEL_COLLECTION,
        "website": WEBSITE_COLLECTION,
    }
    if collection not in valid:
        raise HTTPException(status_code=400, detail=f"Unknown collection: {collection}")
    removed = clear_collection(valid[collection])
    return {"collection": collection, "chunks_removed": removed}


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 9050))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
