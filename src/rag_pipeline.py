from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

from retrieval import search_pdf, search_website
from config import LLM_MODEL


llm = LLM(
    model=LLM_MODEL,
    temperature=0.2
)


@tool("search_pdf_tool")
def search_pdf_tool(query: str):
    """Search the indexed PDF documents for relevant information."""
    return search_pdf(query)


@tool("search_website_tool")
def search_website_tool(query: str):
    """Search the indexed website pages for relevant information."""
    return search_website(query)


agent_router = Agent(
    role="RAG Router",
    goal="Choose correct data source and answer accurately",
    backstory="Routes queries across PDFs and website",
    tools=[search_pdf_tool, search_website_tool],
    llm=llm
)


def run_query(query):

    task = Task(
    description=f"""
User Question: {query}

1 Choose correct source
2 Retrieve information
3 Answer clearly
""",
    expected_output="Clear answer in paragraph format based only on retrieved information.",
    agent=agent_router
)

    crew = Crew(
        agents=[agent_router],
        tasks=[task],
        verbose=False
    )

    result = crew.kickoff()

    return result.raw