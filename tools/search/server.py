from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from search_core import (
    DB_PATH,
    DEFAULT_TOP_K,
    SEARCH_DIR,
    SearchConfigurationError,
    SearchIndex,
    get_embedder,
    index_files,
)

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
except ModuleNotFoundError as exc:
    raise SearchConfigurationError(
        "FastAPI is not installed. Install the packages in tools/search/requirements.txt before "
        "starting the search server."
    ) from exc


STATIC_DIR = SEARCH_DIR / "static"


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    filters: list[str] = Field(default_factory=list)
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=50)


search_index: SearchIndex | None = None


def should_reindex_on_startup() -> bool:
    return os.environ.get("SEARCH_REINDEX_ON_STARTUP", "").lower() in {"1", "true", "yes"}


def initialize_search_index() -> None:
    global search_index
    embedder = get_embedder(os.environ.get("SEARCH_EMBEDDER", "sentence-transformer"))
    if should_reindex_on_startup():
        index_files(
            embedder=embedder,
            db_path=Path(os.environ.get("SEARCH_DB_PATH", DB_PATH)),
            prefer_vec=os.environ.get("SEARCH_DISABLE_SQLITE_VEC", "").lower() not in {"1", "true", "yes"},
        )
    search_index = SearchIndex(
        embedder=embedder,
        db_path=Path(os.environ.get("SEARCH_DB_PATH", DB_PATH)),
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_search_index()
    yield


app = FastAPI(title="Knowledge Base Search", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "ok": True,
        "database": str(Path(os.environ.get("SEARCH_DB_PATH", DB_PATH))),
        "indexed_chunks": len(search_index.chunks) if search_index else 0,
    }


@app.post("/search")
def search(payload: SearchRequest) -> dict[str, object]:
    if search_index is None:
        raise HTTPException(status_code=503, detail="Search index is not ready yet.")

    started_at = time.perf_counter()
    try:
        response = search_index.search(payload.query, payload.filters, payload.top_k)
    except SearchConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    response["took_ms"] = round((time.perf_counter() - started_at) * 1000, 1)
    return response


if __name__ == "__main__":
    try:
        import uvicorn
    except ModuleNotFoundError as exc:
        raise SearchConfigurationError(
            "uvicorn is not installed. Install the packages in tools/search/requirements.txt before "
            "starting the search server."
        ) from exc

    uvicorn.run(
        "server:app",
        host=os.environ.get("SEARCH_HOST", "127.0.0.1"),
        port=int(os.environ.get("SEARCH_PORT", "8000")),
        reload=False,
        app_dir=str(SEARCH_DIR),
    )
