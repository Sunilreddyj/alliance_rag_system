from openai import OpenAI
from retrieval import search_all
from config import LLM_MODEL, OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a knowledgeable assistant. Answer the user's question using ONLY the provided context chunks.

Rules:
- Be specific and detailed when the context supports it.
- If multiple sources mention related info, synthesize them into a coherent answer.
- If the context does not contain enough information to answer, say: "I don't have enough information in the uploaded documents to answer this question."
- Do NOT fabricate facts. Only use what is in the context.
- Format your answer clearly with paragraphs or bullet points where helpful."""


def build_context_string(results):
    if not results:
        return "No relevant context found."

    parts = []
    for i, item in enumerate(results, 1):
        source = item.get("source", "Unknown")
        text = item.get("text", "").strip()
        parts.append(f"[Chunk {i} | Source: {source}]\n{text}")

    return "\n\n---\n\n".join(parts)


def run_query(query):
    results = search_all(query, n_results=6)
    context_str = build_context_string(results)

    user_message = f"""Context:
{context_str}

---

Question: {query}

Answer:"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.1,
        max_tokens=1024
    )

    return response.choices[0].message.content.strip()
