from functools import lru_cache
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from rag.wiki_paths import chroma_dir_has_data, normalize_wiki_base_url, wiki_vector_store_relpath


def vector_index_available(wiki_base_url: str) -> tuple[bool, bool]:
    """
    Indica se existe índice vetorial para a wiki (sem abrir o Chroma).

    Retorna ``(tem_índice, é_legado)``: o segundo é True só se existir ``./chroma_db``
    antigo e não houver pasta ``chroma_dbs/<hash>`` com dados.
    """
    normalized = normalize_wiki_base_url(wiki_base_url)
    persist = Path(wiki_vector_store_relpath(normalized))
    if chroma_dir_has_data(persist):
        return True, False
    legacy = Path("chroma_db")
    if chroma_dir_has_data(legacy):
        return True, True
    return False, False

# Instância única: evita recarregar pesos do modelo a cada ingestão ou primeiro search.
_embeddings: HuggingFaceEmbeddings | None = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    """Retorna o embedder singleton (lazy init na primeira chamada)."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-small", 
            encode_kwargs={"batch_size": 64}
            )
    return _embeddings


def create_vector_db(chunks, wiki_base_url: str):
    """
    Indexa os chunks no Chroma e persiste em disco.

    Usado por ingest.py: normaliza a URL, cria chroma_dbs/<hash> se precisar
    e grava vetores com o mesmo embedding_function usado depois na busca.
    """
    normalized = normalize_wiki_base_url(wiki_base_url)
    persist_directory = wiki_vector_store_relpath(normalized)
    Path(persist_directory).mkdir(parents=True, exist_ok=True)

    texts = [doc.page_content for doc in chunks]
    metadatas = [doc.metadata for doc in chunks]

    db = Chroma.from_documents(
        chunks,
        _get_embeddings(),
        persist_directory=persist_directory,
    )

    db.add_texts(
        texts=texts,
        metadatas=metadatas
    )
    return db


def load_vector_db_for_wiki(wiki_base_url: str) -> tuple[Chroma, bool]:
    """
    Abre o Chroma em modo leitura para uma wiki.

    Retorna (db, used_legacy_store):
    - False no segundo item se usou chroma_dbs/<hash> da wiki;
    - True se caiu no ./chroma_db legado (índice único antigo).

    Levanta FileNotFoundError se não houver dados em nenhum dos dois caminhos.
    """
    normalized = normalize_wiki_base_url(wiki_base_url)
    persist = Path(wiki_vector_store_relpath(normalized))
    emb = _get_embeddings()

    if chroma_dir_has_data(persist):
        return Chroma(persist_directory=str(persist), embedding_function=emb), False

    legacy = Path("chroma_db")
    if chroma_dir_has_data(legacy):
        return Chroma(persist_directory=str(legacy), embedding_function=emb), True

    raise FileNotFoundError(
        f"Nenhum índice encontrado para {normalized}. "
        f"Pasta esperada: {persist}. "
        "Execute a ingestão (ingest.py) com a mesma URL base da wiki."
    )


@lru_cache(maxsize=16)
def get_cached_vector_store(normalized_wiki_url: str) -> tuple[Chroma, bool]:
    """
    Mesmo que load_vector_db_for_wiki, com cache por URL já normalizada.

    Evita reabrir o mesmo persist_directory em toda requisição da API/CLI.
    """
    return load_vector_db_for_wiki(normalized_wiki_url)


def load_vector_db() -> Chroma:
    """Compatível com código antigo: abre apenas ./chroma_db (sem flag legacy)."""
    emb = _get_embeddings()
    return Chroma(persist_directory="./chroma_db", embedding_function=emb)
