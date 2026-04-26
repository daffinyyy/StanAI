from ingestion.ingest_wiki import run_full_wiki_ingest
from rag.wiki_paths import DEFAULT_WIKI_BASE_URL, normalize_wiki_base_url

wiki = normalize_wiki_base_url(DEFAULT_WIKI_BASE_URL)
run_full_wiki_ingest(wiki, log=print)
