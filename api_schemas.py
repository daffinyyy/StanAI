from pydantic import BaseModel, Field, field_validator

from rag.wiki_paths import normalize_wiki_base_url


class ChatRequest(BaseModel):
    """Entrada do POST /chat: wiki + pergunta do usuário."""

    wiki_url: str = Field(
        ...,
        min_length=4,
        max_length=2048,
        examples=["https://sua-wiki.fandom.com"],
    )
    message: str = Field(..., min_length=1, max_length=8000)

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
