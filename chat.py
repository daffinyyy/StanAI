import os

from rag.embeddings import get_cached_vector_store
from rag.llm import get_llm
from rag.query import run_rag_query
from rag.wiki_paths import DEFAULT_WIKI_BASE_URL, normalize_wiki_base_url

wiki = normalize_wiki_base_url(
    os.environ.get("STANAI_WIKI_URL", DEFAULT_WIKI_BASE_URL)
)
db, _legacy = get_cached_vector_store(wiki)
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


    answer, _sources = run_rag_query(db, llm, query)

    print("\n🦫 Stan:", answer, "\n")
