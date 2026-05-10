"""
Orchestrator Agent — routes user queries to PDF, Excel, or Website agents,
merges results, then calls the LLM to generate a final answer.
"""
import re
from openai import OpenAI
from agents import pdf_agent, excel_agent, website_agent
from config import OPENAI_API_KEY, LLM_MODEL
from vectorstore.chroma_store import collection_stats

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a knowledgeable AI assistant for Alliance University.
Answer the user's question using ONLY the provided context chunks.

Rules:
- Be specific and detailed when the context supports it.
- If multiple sources mention related info, synthesize them into a coherent answer.
- If the context does not contain enough information, say: "I don't have enough information in the indexed documents to answer this question."
- Do NOT fabricate facts. Only use what is in the context.
- Format your answer clearly with paragraphs or numbered lists where helpful.
- Always mention the source(s) you used at the end in a "Sources:" section."""


# Keyword sets used for routing decisions
EXCEL_KEYWORDS = {
    "table", "spreadsheet", "excel", "csv", "sheet", "row", "column",
    "data", "fee", "fees", "structure", "schedule", "list", "seats",
    "intake", "quota", "statistic", "figure", "number", "amount",
}
PDF_KEYWORDS = {
    "pdf", "document", "policy", "rule", "regulation", "guideline",
    "brochure", "handbook", "syllabus", "curriculum", "prospectus",
    "form", "application", "procedure", "criteria",
}
WEBSITE_KEYWORDS = {
    "website", "online", "web", "page", "portal", "site", "link",
    "admission", "course", "program", "department", "faculty",
    "contact", "address", "location", "deadline", "event", "news",
}


def _classify_query(query: str) -> dict:
    """Return weights for each source based on keyword overlap."""
    tokens = set(re.findall(r"\b\w+\b", query.lower()))
    excel_score = len(tokens & EXCEL_KEYWORDS)
    pdf_score = len(tokens & PDF_KEYWORDS)
    website_score = len(tokens & WEBSITE_KEYWORDS)

    # If no strong signal, search all
    if excel_score == 0 and pdf_score == 0 and website_score == 0:
        return {"pdf": True, "excel": True, "website": True, "reason": "broad"}

    return {
        "pdf": pdf_score > 0 or (excel_score == 0 and website_score == 0),
        "excel": excel_score > 0,
        "website": website_score > 0 or pdf_score == 0,
        "reason": f"pdf={pdf_score} excel={excel_score} web={website_score}",
    }


def _build_context(results: list) -> str:
    if not results:
        return "No relevant context found."
    parts = []
    for i, item in enumerate(results, 1):
        source = item.get("source", "Unknown")
        text = item.get("text", "").strip()
        src_type = item.get("type", "")
        parts.append(f"[Chunk {i} | Source: {source} | Type: {src_type}]\n{text}")
    return "\n\n---\n\n".join(parts)


def run_query(query: str, n_per_source: int = 6) -> dict:
    stats = collection_stats()
    routing = _classify_query(query)

    all_results = []

    if routing.get("pdf") and stats.get("pdf_documents", 0) > 0:
        all_results.extend(pdf_agent.search(query, n_per_source))

    if routing.get("excel") and stats.get("excel_documents", 0) > 0:
        all_results.extend(excel_agent.search(query, n_per_source))

    if routing.get("website") and stats.get("website_documents", 0) > 0:
        all_results.extend(website_agent.search(query, n_per_source))

    # Fallback: if primary routing returns nothing, try all sources
    if not all_results:
        all_results.extend(pdf_agent.search(query, n_per_source))
        all_results.extend(excel_agent.search(query, n_per_source))
        all_results.extend(website_agent.search(query, n_per_source))

    # Deduplicate and sort by score descending
    seen_texts = set()
    unique_results = []
    for r in sorted(all_results, key=lambda x: x.get("score", 0), reverse=True):
        if r["text"] not in seen_texts:
            seen_texts.add(r["text"])
            unique_results.append(r)

    top_results = unique_results[:10]
    context_str = _build_context(top_results)

    user_message = f"""Context:\n{context_str}\n\n---\n\nQuestion: {query}\n\nAnswer:"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        max_tokens=1200,
    )

    answer = response.choices[0].message.content.strip()

    sources = list({r["source"] for r in top_results})

    return {
        "answer": answer,
        "sources": sources,
        "routing": routing.get("reason", ""),
        "chunks_used": len(top_results),
    }
