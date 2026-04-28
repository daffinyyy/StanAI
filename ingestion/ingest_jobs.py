"""Jobs de ingestão em memória (um processo); use fila externa se tiver vários workers."""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field

from rag.embeddings import get_cached_vector_store, vector_index_available
from rag.wiki_paths import wiki_index_job_id

from ingestion.ingest_wiki import run_full_wiki_ingest

_log = logging.getLogger(__name__)


@dataclass
class IngestJob:
    job_id: str
    wiki_base_url: str
    status: str  # queued | running | completed | failed
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    finished_at: float | None = None


_lock = threading.Lock()
_jobs: dict[str, IngestJob] = {}
_worker_locks: dict[str, threading.Lock] = {}


def _lock_for_job(job_id: str) -> threading.Lock:
    with _lock:
        if job_id not in _worker_locks:
            _worker_locks[job_id] = threading.Lock()
        return _worker_locks[job_id]


def get_ingest_job(job_id: str) -> IngestJob | None:
    with _lock:
        return _jobs.get(job_id)


def _set_job_fields(job_id: str, **kwargs: object) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        for k, v in kwargs.items():
            setattr(job, k, v)


def _worker(job_id: str) -> None:
    wl = _lock_for_job(job_id)
    with wl:
        with _lock:
            job = _jobs.get(job_id)
            if not job or job.status != "queued":
                return
            job.status = "running"
            job.error = None
            wiki = job.wiki_base_url

    try:
        run_full_wiki_ingest(wiki, log=_log.info)
        _set_job_fields(job_id, status="completed", error=None)
    except Exception as exc:  # noqa: BLE001 — registro no job
        _set_job_fields(job_id, status="failed", error=str(exc))
    finally:
        _set_job_fields(job_id, finished_at=time.time())
        get_cached_vector_store.cache_clear()


def start_ingest_if_needed(normalized_wiki_url: str) -> tuple[IngestJob, bool]:
    """
    Garante um job ``queued|running`` para a wiki ou devolve o estado atual.

    Retorna ``(job, iniciou_worker)``. O worker é uma thread daemon no mesmo processo.
    """
    job_id = wiki_index_job_id(normalized_wiki_url)

    with _lock:
        existing = _jobs.get(job_id)
        if existing:
            if existing.status in ("queued", "running"):
                return existing, False
            if existing.status == "completed" and vector_index_available(normalized_wiki_url)[0]:
                return existing, False

        job = IngestJob(job_id=job_id, wiki_base_url=normalized_wiki_url, status="queued")
        _jobs[job_id] = job

    threading.Thread(target=_worker, args=(job_id,), daemon=True).start()
    return job, True

