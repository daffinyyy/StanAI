import hashlib
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_WIKI_BASE_URL = "https://viscera-cleanup-detail.fandom.com"


# normaliza a url da wiki (ex.: https://algo.fandom.com)
def normalize_wiki_base_url(url: str) -> str:
    u = (url or "").strip()
    if not u:
        raise ValueError("wiki_url vazio")
    if not u.lower().startswith(("http://", "https://")):
        u = "https://" + u
    parsed = urlparse(u)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("wiki_url inválida")
    scheme = (parsed.scheme or "https").lower()
    if scheme not in ("http", "https"):
        raise ValueError("wiki_url: use http ou https")
    host = parsed.netloc.lower()
    return f"{scheme}://{host}".rstrip("/")


# retorna o caminho para o banco de dados do Chroma (ex.: chroma_dbs/1234567890)
def wiki_vector_store_relpath(wiki_url: str) -> str:
    normalized = normalize_wiki_base_url(wiki_url)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return str(Path("chroma_dbs") / digest)


# verifica se o diretório do Chroma contém dados (ex.: chroma_dbs/1234567890)
def chroma_dir_has_data(path: Path) -> bool:
    if not path.is_dir():
        return False
    sqlite = path / "chroma.sqlite3"
    if sqlite.is_file():
        return True
    return any(path.iterdir())
