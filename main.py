from ingestion.fetch_pages import fetch_page
from ingestion.get_pages import get_all_pages
from ingestion.clean_text import clean_html
from rag.chunking import create_documents, chunk_documents
from rag.embeddings import create_vector_db, search
from rag.llm import get_llm, generate_answer


fandom_url = "https://undertale.fandom.com"
api_url = fandom_url + "/api.php"
data = get_all_pages(fandom_url)
titles = data["titles"][:15]  # começa pequeno


#pegar as paginas e limpar
pages = []
for i, title in enumerate(titles):
    print(f"[{i+1}] Processando: {title}")

    html = fetch_page(api_url, title)
    if not html:
        continue

    text = clean_html(html)

    if len(text) < 50:
        continue

    pages.append({
        "title": title,
        "text": text
    })


#chunk
documents = create_documents(pages, fandom_url)
chunks = chunk_documents(documents)
print("\nChunks gerados:", len(chunks))

#embbeding
db = create_vector_db(chunks)

#teste
query = "quantas conquistas tem o jogo"
query_en = "how many achievements"

results = search(db, query_en, k=10)
unique_results = []
seen_titles = set()

for r in results:
    title = r.metadata["title"]

    if title not in seen_titles:
        unique_results.append(r)
        seen_titles.add(title)

    if len(unique_results) == 3:
        break

context = "\n\n".join([r.page_content for r in unique_results])

llm = get_llm()
answer = generate_answer(llm, query, context)

print("\n--- RESPOSTA ---\n")
print(answer)