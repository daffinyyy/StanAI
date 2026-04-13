from rag.embeddings import load_vector_db
from rag.llm import get_llm, generate_answer

db = load_vector_db()
llm = get_llm()

print("Chat iniciado (digite 'sair' pra parar)\n")

while True:
    query = input(">> ")

    if query.lower() == "sair":
        break

    # 🔍 DEBUG
    # print("\n🔍 DEBUG EMBEDDING (similarity_search_with_score):")
    # debug_results = db.similarity_search_with_score(query, k=5)
    # for doc, score in debug_results:
    #     print(f"\nScore: {score}")
    #     print("Metadata:", doc.metadata)


    results = db.similarity_search(query, k=10)

    #deduplica
    unique_results = []
    seen_titles = set()

    for r in results:
        title = r.metadata["title"]

        if title not in seen_titles:
            unique_results.append(r)
            seen_titles.add(title)

        if len(unique_results) == 7:
            break

    context = ""
    for r in results[:7]:
        title = r.metadata["title"]
        section = r.metadata.get("section", "")

        context += f"\n[Título: {title} | Seção: {section}]\n"
        context += r.page_content + "\n\n"

    #DEBUG  
    # print("\n===== CONTEXTO REAL =====\n")
    # print(context)

    answer = generate_answer(llm, query, context)

    print("\n🦫 Stan:", answer, "\n")