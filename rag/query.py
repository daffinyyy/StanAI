from langchain_core.vectorstores import VectorStore

from rag.llm import generate_answer


def run_rag_query(db: VectorStore, llm, query: str) -> tuple[str, list[dict]]:
    """
    Executa busca semelhante no vetor store, monta contexto e gera a resposta.

    Busca os k=10 chunks mais próximos, deduplica por ``metadata["title"]``
    (até 7 páginas distintas) para não repetir o mesmo artigo no prompt,
    monta um bloco de contexto com título/seção e chama ``generate_answer``.

    Retorna ``(answer, sources)`` onde ``sources`` é uma lista de
    ``{"title", "section"}`` alinhada aos trechos usados no contexto.
    """
    results = db.similarity_search(query, k=15)

    unique_results: list = []
    seen_titles: set[str] = set()

    for r in results:
        title = r.metadata["title"]
        if title not in seen_titles:
            unique_results.append(r)
            seen_titles.add(title)
        if len(unique_results) == 7:
            break

    context = ""
    sources: list[dict] = []

    for r in unique_results:
        title = r.metadata["title"]
        section = str(r.metadata.get("section") or "")

        context += f"\n[Título: {title} | Seção: {section}]\n"
        context += r.page_content + "\n\n"
        sources.append({"title": title, "section": section})

    answer = generate_answer(llm, query, context)
    return answer, sources