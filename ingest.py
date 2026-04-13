from ingestion.fetch_pages import fetch_page
from ingestion.get_pages import get_all_pages
from ingestion.clean_text import clean_html

from rag.chunking import create_documents, chunk_documents
from rag.embeddings import create_vector_db

# config
fandom_url = "https://viscera-cleanup-detail.fandom.com"
api_url = fandom_url + "/api.php"

print("Buscando páginas...")
data = get_all_pages(fandom_url)
titles = data["titles"]

pages = []

print("Baixando e limpando...")

for i, title in enumerate(titles):
    print(f"[{i+1}/{len(titles)}] {title}")

    html = fetch_page(api_url, title)

    if not html:
        continue

    text = clean_html(html, page_title=title)

    if len(text.strip()) < 30:
        continue

    pages.append({
        "title": title,
        "text": text
    })

print("Criando documentos...")
documents = create_documents(pages, fandom_url)

print("Criando chunks...")
chunks = chunk_documents(documents)

print("Gerando embeddings e salvando DB...")
db = create_vector_db(chunks)

print("Ingestão concluída!")