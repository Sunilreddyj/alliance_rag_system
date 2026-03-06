import uuid
import requests
import fitz
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import chromadb

from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHROMA_DB_PATH, EMBED_MODEL

embed_model = SentenceTransformer(EMBED_MODEL)

chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

pdf_store = chroma_client.get_or_create_collection(name="alliance_pdf_rag")
website_store = chroma_client.get_or_create_collection(name="alliance_website_rag")


def embed_text(text):
    return embed_model.encode(text).tolist()


def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
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

    raw_text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(raw_text)

    for chunk in chunks:
        pdf_store.add(
            documents=[chunk],
            ids=[str(uuid.uuid4())],
            embeddings=[embed_text(chunk)]
        )


def fetch_website_text(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    return soup.get_text(separator=" ").strip()


def index_website_pages(urls):

    for url in urls:
        text = fetch_website_text(url)

        chunks = chunk_text(text)

        for chunk in chunks:
            website_store.add(
                documents=[chunk],
                ids=[str(uuid.uuid4())],
                embeddings=[embed_text(chunk)],
                metadatas=[{"source": url}]
            )