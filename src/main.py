import os
import sys

# Ensure src/ is on the path when running from project root
sys.path.insert(0, os.path.dirname(__file__))

from ingestion import store_local_pdf, store_uploaded_pdfs, index_website_pages, clear_user_pdfs
from rag_pipeline import run_query
import gradio as gr

# ── Startup indexing (skipped automatically if already indexed) ──────────────
store_local_pdf("data/policy.pdf")

index_website_pages([
    "https://www.alliance.edu.in/admissions/courses-fee-structure",
    "https://www.alliance.edu.in/admissions",
])


# ── Handlers ─────────────────────────────────────────────────────────────────

def handle_upload(files, clear_prev):
    if not files:
        return "⚠ No files selected. Please choose one or more PDF files."

    paths = [f.name for f in files] if hasattr(files[0], "name") else files
    lines = store_uploaded_pdfs(paths, clear_existing=clear_prev)
    total_chunks = sum(
        int(l.split(":")[1].strip().split(" ")[0])
        for l in lines if l.startswith("✓") and "chunks" in l
    ) if lines else 0

    summary = "\n".join(lines)
    summary += f"\n\n📚 Total new chunks indexed: {total_chunks}" if total_chunks else ""
    return summary


def handle_query(query):
    query = query.strip()
    if not query:
        return "Please enter a question."
    try:
        return run_query(query)
    except Exception as e:
        return f"Error: {str(e)}"


def handle_clear():
    try:
        clear_user_pdfs()
        return "✓ All uploaded PDFs cleared from the index."
    except Exception as e:
        return f"Error clearing PDFs: {str(e)}"


# ── Gradio UI ─────────────────────────────────────────────────────────────────

CSS = """
.upload-box { border: 2px dashed #4a90d9 !important; border-radius: 8px !important; }
.answer-box textarea { font-size: 15px !important; line-height: 1.6 !important; }
"""

with gr.Blocks(title="RAG System", css=CSS, theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
# 📄 RAG — Document Q&A System
Upload your PDFs, then ask questions. The system will find the most relevant chunks and generate a precise answer.
""")

    with gr.Tab("📤 Upload PDFs"):
        gr.Markdown("### Upload one or more PDF files to index them for Q&A")
        pdf_files = gr.File(
            label="Select PDF Files",
            file_count="multiple",
            file_types=[".pdf"],
            elem_classes=["upload-box"]
        )
        clear_checkbox = gr.Checkbox(
            label="Clear previously uploaded PDFs before indexing",
            value=False
        )
        with gr.Row():
            upload_btn = gr.Button("⚡ Process & Index PDFs", variant="primary", scale=2)
            clear_btn = gr.Button("🗑 Clear All Uploaded PDFs", variant="stop", scale=1)

        upload_status = gr.Textbox(
            label="Indexing Status",
            lines=8,
            interactive=False,
            placeholder="Status will appear here after upload..."
        )

        upload_btn.click(
            fn=handle_upload,
            inputs=[pdf_files, clear_checkbox],
            outputs=upload_status
        )
        clear_btn.click(
            fn=handle_clear,
            inputs=[],
            outputs=upload_status
        )

    with gr.Tab("💬 Ask a Question"):
        gr.Markdown("### Ask anything from the indexed documents")
        query_box = gr.Textbox(
            lines=3,
            label="Your Question",
            placeholder="e.g. What are the fee structures? What is the admission process?"
        )
        ask_btn = gr.Button("🔍 Get Answer", variant="primary")
        answer_box = gr.Textbox(
            lines=15,
            label="Answer",
            interactive=False,
            elem_classes=["answer-box"],
            placeholder="Your answer will appear here..."
        )
        ask_btn.click(fn=handle_query, inputs=query_box, outputs=answer_box)
        query_box.submit(fn=handle_query, inputs=query_box, outputs=answer_box)

    with gr.Tab("ℹ️ About"):
        gr.Markdown("""
## How it works

1. **Upload PDFs** — Select one or more PDF files in the *Upload PDFs* tab and click **Process & Index PDFs**.
   - Each PDF is split into overlapping chunks (600 chars, 120 overlap) for precise retrieval.
   - Chunks are embedded with `mxbai-embed-large-v1` and stored in ChromaDB.

2. **Ask questions** — Type your question in the *Ask a Question* tab.
   - The system searches all indexed sources (uploaded PDFs + default policy PDF + website).
   - Top matching chunks are sent to **GPT-4o-mini** with a strict factual prompt.
   - The answer is based only on what's in your documents.

3. **Clear uploads** — Use the *Clear All Uploaded PDFs* button to reset user-uploaded documents.

> The default Alliance University policy PDF and website are always available even if you haven't uploaded anything.
""")


port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
