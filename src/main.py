from ingestion import store_local_pdf, index_website_pages
from rag_pipeline import run_query
import gradio as gr

# index local PDF
store_local_pdf("data/BTECH 2026.pdf")

# index website pages
base_url = "https://www.alliance.edu.in/admissions/courses-fee-structure"

index_website_pages([
    base_url,
    base_url + "/admissions",
    base_url + "/fees"
])

def rag_interface(query):
    try:
        return run_query(query)
    except Exception as e:
        return str(e)

iface = gr.Interface(
    fn=rag_interface,
    inputs=gr.Textbox(lines=5),
    outputs="text",
    title="Alliance University RAG System"
)

iface.launch()