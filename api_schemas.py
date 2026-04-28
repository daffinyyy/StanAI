from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, field_validator

from rag.wiki_paths import normalize_wiki_base_url


class ChatRequest(BaseModel):
    """Entrada do POST /chat: wiki + pergunta do usuário."""

    wiki_url: str = Field(
        ...,
        min_length=4,
        max_length=2048,
        validation_alias=AliasChoices("wiki_url", "url", "page_url"),
        description=(
            "URL base da wiki Fandom ou URL da página atual (path/query são ignorados; "
            "o RAG usa o mesmo Chroma por domínio)."
        ),
        examples=[
            "https://sua-wiki.fandom.com",
            "https://sua-wiki.fandom.com/wiki/Nome_do_artigo",
        ],
    )
    message: str = Field(..., min_length=1, max_length=8000)

    auto_ingest: bool = Field(
        True,
        description=(
            "Se não existir índice Chroma para a wiki, inicia ingestão em background "
            "e a API responde 202 com job_id e status_url até concluir."
        ),
    )

    @field_validator("wiki_url")
    @classmethod
    def wiki_url_normalizado(cls, v: str) -> str:
        """Garante scheme/host válidos"""
        return normalize_wiki_base_url(v)


class SourceItem(BaseModel):
    """Uma fonte citável retornada ao client (metadados do chunk RAG)"""

    title: str
    section: str


class ChatResponse(BaseModel):
    """Saída do POST /chat: resposta, fontes e se caiu no índice legado ./chroma_db."""

    wiki_url: str
    answer: str
    sources: list[SourceItem]
    used_legacy_vector_store: bool = False


class IngestPendingResponse(BaseModel):
    """Corpo quando POST /chat retorna 202: índice sendo criado em background."""

    indexing: Literal[True] = True
    job_id: str
    wiki_base_url: str
    message: str
    status_url: str


class IngestJobStatusResponse(BaseModel):
    """Estado de um job de ingestão (GET /ingest/jobs/{job_id})."""

    job_id: str
    wiki_base_url: str
    status: Literal["queued", "running", "completed", "failed"]
    error: str | None = None
    created_at: float
    finished_at: float | None = None
