from crewai.tools import BaseTool
from pydantic import Field
from langchain_ollama import ChatOllama
from duckduckgo_search import DDGS

from rag.embeddings import get_cached_vector_store
from rag.query import run_rag_query


class WikiRAGTool(BaseTool):
    name: str = "Wiki RAG Search"
    description: str = ("Busca informações na wiki indexada através do banco vetorial.")
    wiki_url: str = Field(description="URL base da wiki utilizada pelo StanAI.")

    def _run(self, question: str) -> str:
        db, _ = get_cached_vector_store(self.wiki_url)

        rag_llm = ChatOllama(
            model="qwen2:7b"
        )

        answer, sources = run_rag_query(
            db=db,
            llm=rag_llm,
            query=question
)

        source_text = "\n".join(
            [
                f"- {s['title']} ({s['section']})"
                for s in sources
            ]
        )

        return f"""
            Resposta encontrada na wiki:

            {answer}

            Fontes:
            {source_text}
        """
    

class WebSearchTool(BaseTool):
    name: str = "Web Search"
    description: str = (
        "Pesquisa informações recentes na internet."
    )

    def _run(self, query: str) -> str:

        results = []

        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append(
                    f"Título: {r['title']}\n"
                    f"Resumo: {r['body']}\n"
                    f"URL: {r['href']}\n"
                )

        return "\n\n".join(results)