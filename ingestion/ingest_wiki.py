"""Ingestão completa de uma wiki Fandom (MediaWiki com ``/api.php`` na raiz do host)."""

from __future__ import annotations

import logging
from collections.abc import Callable

from ingestion.clean_text import clean_html
from ingestion.fetch_pages import fetch_page
from ingestion.get_pages import get_all_pages

from rag.chunking import chunk_documents, create_documents
from rag.embeddings import create_vector_db
from rag.wiki_paths import normalize_wiki_base_url

logger = logging.getLogger(__name__)


def run_full_wiki_ingest(
    wiki_base_url: str,
    *,
    log: Callable[[str], None] | None = None,
) -> None:
    """
    Baixa todas as páginas (namespace 0), gera chunks e persiste o Chroma em
    ``chroma_dbs/<hash>`` para a origem normalizada de ``wiki_base_url``.
    """
    out = log or logger.info

    normalized = normalize_wiki_base_url(wiki_base_url)
    api_url = normalized.rstrip("/") + "/api.php"

    out("Buscando páginas...")
    data = get_all_pages(normalized)
    titles = data["titles"]
    pages: list[dict] = []

    out("Baixando e limpando...")
    for i, title in enumerate(titles):
        out(f"[{i + 1}/{len(titles)}] {title}")
        html = fetch_page(api_url, title)
        if not html:
            continue
        text = clean_html(html, page_title=title)
        if len(text.strip()) < 30:
            continue
        pages.append({"title": title, "text": text})

    out("Criando documentos...")
    documents = create_documents(pages, normalized)

    out("Criando chunks...")
    chunks = chunk_documents(documents)

    out("Gerando embeddings e salvando DB...")
    create_vector_db(chunks, normalized)
    out("Ingestão concluída.")
