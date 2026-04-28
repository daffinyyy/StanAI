from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api_schemas import (
    ChatRequest,
    ChatResponse,
    IngestJobStatusResponse,
    IngestPendingResponse,
    SourceItem,
)
from ingestion.ingest_jobs import get_ingest_job, start_ingest_if_needed
from rag.embeddings import get_cached_vector_store, vector_index_available
from rag.llm import get_llm
from rag.query import run_rag_query


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm = get_llm()
    yield


app = FastAPI(
    title="StanAI",
    description=(
        "API de chat RAG: envie a URL da wiki (origem ou qualquer página) e a pergunta. "
        "A origem (scheme+host) define chroma_dbs/<hash>. "
        "Sem índice e com auto_ingest, a ingestão roda em background (veja GET /ingest/jobs/{job_id})."
    ),
    lifespan=lifespan,
)

# Permite configurar origens via env (ex.: STANAI_CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173").
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "STANAI_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Endpoint de saúde para monitoramento."""
    return {"status": "ok"}


@app.get("/ingest/jobs/{job_id}", response_model=IngestJobStatusResponse)
async def ingest_job_status(job_id: str):
    """Consulta o estado de um job de ingestão disparado pelo POST /chat (memória do processo)."""
    job = get_ingest_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    return IngestJobStatusResponse(
        job_id=job.job_id,
        wiki_base_url=job.wiki_base_url,
        status=job.status,
        error=job.error,
        created_at=job.created_at,
        finished_at=job.finished_at,
    )


@app.post(
    "/chat",
    responses={
        200: {"description": "Resposta RAG", "model": ChatResponse},
        202: {"description": "Ingestão em andamento; consulte GET /ingest/jobs/{job_id}", "model": IngestPendingResponse},
    },
)
async def chat(body: ChatRequest, request: Request):
    """
    Chat RAG: com índice existente devolve 200. Sem índice e ``auto_ingest=true``,
    inicia job em background e devolve 202 até o cliente repetir o POST após ``completed``.
    """
    wiki = body.wiki_url

    try:
        has_idx, _ = vector_index_available(wiki)
        if not has_idx:
            if not body.auto_ingest:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Nenhum índice Chroma para esta wiki. "
                        "Ative auto_ingest ou rode a ingestão manualmente."
                    ),
                )
            job, _ = start_ingest_if_needed(wiki)
            pending = IngestPendingResponse(
                job_id=job.job_id,
                wiki_base_url=job.wiki_base_url,
                message=(
                    "Índice em construção. Faça GET no status_url até status ser "
                    "'completed' (ou 'failed'); em seguida envie POST /chat novamente."
                ),
                status_url=f"/ingest/jobs/{job.job_id}",
            )
            return JSONResponse(status_code=202, content=pending.model_dump())

        db, legacy = get_cached_vector_store(wiki)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
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
