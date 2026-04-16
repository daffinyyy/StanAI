from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request

from api_schemas import ChatRequest, ChatResponse, SourceItem
from rag.embeddings import get_cached_vector_store
from rag.llm import get_llm
from rag.query import run_rag_query


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ChatOllama ligado ao Ollama local, evita recriar o cliente a cada POST(espero que funcione)
    app.state.llm = get_llm()
    yield


app = FastAPI(
    title="StanAI",
    description="API de chat RAG: envie a URL base da wiki e a pergunta. O índice fica em chroma_dbs/<hash>.",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    """Endpoint de saúde para monitoramento."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request):
    """
    Endpoint de chat RAG: recebe URL da wiki e pergunta, retorna resposta e fontes.
    """
    wiki = body.wiki_url
    try:
        db, legacy = get_cached_vector_store(wiki)
    except ValueError as exc:
        # url invalida ou rejeitada pelo normalizador
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        # nao existe pasta chroma_dbs/<hash
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        answer, sources = run_rag_query(
            db,
            request.app.state.llm,
            body.message.strip(),
        )
    except Exception as exc:  # noqa: BLE001 — fronteira HTTP
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ChatResponse(
        wiki_url=wiki,
        answer=answer,
        sources=[SourceItem(**s) for s in sources],
        used_legacy_vector_store=legacy,
    )
