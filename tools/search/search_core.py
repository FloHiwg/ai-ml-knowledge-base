from __future__ import annotations

import argparse
import hashlib
import math
import os
import re
import sqlite3
import struct
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Protocol, Sequence
from urllib.parse import quote


REPO_ROOT = Path(__file__).resolve().parents[2]
VAULT_ROOT = REPO_ROOT / "knowledge-base"
SEARCH_DIR = Path(__file__).resolve().parent
DB_PATH = SEARCH_DIR / "search.db"
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_VECTOR_DIM = 384
DEFAULT_TOP_K = 10
DEFAULT_MIN_CHARS = 100
DEFAULT_MAX_CHARS = 800
SEMANTIC_SCORE_THRESHOLD = 0.32
SECTION_DIRECTORIES = {
    "manual": "manual",
    "summaries": "summary",
    "wiki": "wiki",
}
ALLOWED_FILTERS = frozenset(SECTION_DIRECTORIES.values())
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_-]*", re.IGNORECASE)
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


class SearchConfigurationError(RuntimeError):
    pass


class Embedder(Protocol):
    model_name: str
    dimension: int

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...


@dataclass(frozen=True)
class ChunkRecord:
    file_path: str
    section_title: str
    section_type: str
    text: str
    char_offset: int
    file_mtime: float


@dataclass(frozen=True)
class SearchResult:
    file_path: str
    section_title: str
    section_type: str
    snippet: str
    score: float | None
    match_type: str
    char_offset: int

    @property
    def obsidian_url(self) -> str:
        path_without_suffix = self.file_path[:-3] if self.file_path.endswith(".md") else self.file_path
        return f"obsidian://open?vault=knowledge-base&file={quote(path_without_suffix, safe='/')}"

    def as_dict(self) -> dict[str, object]:
        return {
            "file_path": self.file_path,
            "section_title": self.section_title,
            "section_type": self.section_type,
            "snippet": self.snippet,
            "score": self.score,
            "match_type": self.match_type,
            "char_offset": self.char_offset,
            "obsidian_url": self.obsidian_url,
        }


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME) -> None:
        self.model_name = model_name
        self.dimension = DEFAULT_VECTOR_DIM
        try:
            from sentence_transformers import SentenceTransformer
        except ModuleNotFoundError as exc:
            raise SearchConfigurationError(
                "sentence-transformers is not installed. Install the packages in "
                "tools/search/requirements.txt or use --embedder hash for a lightweight fallback."
            ) from exc
        try:
            self._model = SentenceTransformer(model_name, local_files_only=True)
        except Exception as local_error:
            try:
                self._model = SentenceTransformer(model_name, local_files_only=False)
            except Exception as remote_error:
                raise SearchConfigurationError(
                    "Unable to load the embedding model. If you already downloaded it once, rerun in the "
                    "same environment and keep the local cache. Otherwise allow a one-time model download."
                ) from remote_error

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self._model.encode(
            list(texts),
            normalize_embeddings=True,
            show_progress_bar=len(texts) >= 32,
        )
        return [list(map(float, row)) for row in embeddings.tolist()]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class HashingEmbedder:
    def __init__(self, dimension: int = DEFAULT_VECTOR_DIM) -> None:
        self.model_name = f"hashing-{dimension}"
        self.dimension = dimension

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        tokens = tokenize(text)
        if not tokens:
            return vector
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=16).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            weight = 1.0 + (digest[5] / 255.0)
            vector[index] += sign * weight
        return normalize_vector(vector)


def get_embedder(kind: str = "sentence-transformer") -> Embedder:
    if kind == "sentence-transformer":
        return SentenceTransformerEmbedder()
    if kind == "hash":
        return HashingEmbedder()
    raise SearchConfigurationError(f"Unsupported embedder: {kind}")


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def normalize_vector(values: Sequence[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        return [0.0 for _ in values]
    return [float(value / norm) for value in values]


def serialize_vector(values: Sequence[float]) -> bytes:
    return struct.pack(f"<{len(values)}f", *values)


def deserialize_vector(blob: bytes, dimension: int) -> list[float]:
    if len(blob) != dimension * 4:
        raise ValueError(f"Expected {dimension * 4} bytes for vector, got {len(blob)}")
    return list(struct.unpack(f"<{dimension}f", blob))


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def infer_section_type(relative_path: str) -> str:
    top_level = Path(relative_path).parts[0]
    if top_level not in SECTION_DIRECTORIES:
        raise SearchConfigurationError(f"Unsupported section directory for indexing: {relative_path}")
    return SECTION_DIRECTORIES[top_level]


def collect_markdown_files(vault_root: Path = VAULT_ROOT) -> list[Path]:
    files: list[Path] = []
    for directory_name in SECTION_DIRECTORIES:
        directory = vault_root / directory_name
        if not directory.exists():
            continue
        files.extend(sorted(directory.rglob("*.md")))
    return files


def extract_sections(text: str, default_section: str) -> list[tuple[str, str, int]]:
    if not text.strip():
        return []

    matches = list(HEADING_RE.finditer(text))
    sections: list[tuple[str, str, int]] = []

    if not matches:
        return [(extract_document_title(text) or default_section, text, 0)]

    leading = text[: matches[0].start()]
    if leading.strip():
        sections.append((extract_document_title(leading) or default_section, leading, 0))

    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((title, text[start:end], start))
    return sections


def extract_document_title(text: str) -> str | None:
    match = TITLE_RE.search(text)
    return match.group(1).strip() if match else None


def trim_text_with_offset(text: str, char_offset: int) -> tuple[str, int]:
    leading_trimmed = len(text) - len(text.lstrip())
    trimmed = text.strip()
    return trimmed, char_offset + leading_trimmed


def paragraph_spans(text: str) -> list[tuple[str, int]]:
    spans: list[tuple[str, int]] = []
    for match in re.finditer(r"\S[\s\S]*?(?=\n\s*\n|\Z)", text):
        chunk, offset = trim_text_with_offset(match.group(0), match.start())
        if chunk:
            spans.append((chunk, offset))
    return spans


def sentence_spans(text: str) -> list[tuple[str, int]]:
    spans: list[tuple[str, int]] = []
    start = 0
    for match in re.finditer(r"(?<=[.!?])\s+", text):
        segment = text[start : match.start()]
        segment, offset = trim_text_with_offset(segment, start)
        if segment:
            spans.append((segment, offset))
        start = match.end()
    tail, offset = trim_text_with_offset(text[start:], start)
    if tail:
        spans.append((tail, offset))
    return spans


def fixed_width_spans(text: str, start_offset: int, max_chars: int) -> list[tuple[str, int]]:
    spans: list[tuple[str, int]] = []
    cursor = 0
    while cursor < len(text):
        end = min(len(text), cursor + max_chars)
        if end < len(text):
            candidate = text[cursor:end]
            last_space = max(candidate.rfind(" "), candidate.rfind("\n"))
            if last_space > max_chars // 2:
                end = cursor + last_space
        segment, offset = trim_text_with_offset(text[cursor:end], start_offset + cursor)
        if segment:
            spans.append((segment, offset))
        if end <= cursor:
            end = min(len(text), cursor + max_chars)
        cursor = end
    return spans


def split_long_span(text: str, start_offset: int, max_chars: int) -> list[tuple[str, int]]:
    if len(text) <= max_chars:
        segment, offset = trim_text_with_offset(text, start_offset)
        return [(segment, offset)] if segment else []

    sentences = sentence_spans(text)
    if len(sentences) <= 1:
        return fixed_width_spans(text, start_offset, max_chars)

    chunks: list[tuple[str, int]] = []
    current_parts: list[str] = []
    current_start = start_offset
    current_length = 0

    def flush() -> None:
        nonlocal current_parts, current_start, current_length
        if not current_parts:
            return
        combined = " ".join(current_parts)
        combined, adjusted_offset = trim_text_with_offset(combined, current_start)
        if combined:
            chunks.append((combined, adjusted_offset))
        current_parts = []
        current_start = start_offset
        current_length = 0

    for sentence, sentence_offset in sentences:
        if len(sentence) > max_chars:
            flush()
            chunks.extend(fixed_width_spans(sentence, sentence_offset, max_chars))
            continue
        separator = 1 if current_parts else 0
        if current_parts and current_length + separator + len(sentence) > max_chars:
            flush()
        if not current_parts:
            current_start = sentence_offset
        current_parts.append(sentence)
        current_length += separator + len(sentence)
    flush()
    return chunks


def split_section_text(
    text: str,
    start_offset: int,
    min_chars: int = DEFAULT_MIN_CHARS,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> list[tuple[str, int]]:
    text, start_offset = trim_text_with_offset(text, start_offset)
    if not text:
        return []
    if len(text) <= max_chars:
        return [(text, start_offset)] if len(text) >= min_chars else []

    paragraphs = paragraph_spans(text)
    if not paragraphs:
        return []

    chunks: list[tuple[str, int]] = []
    current_parts: list[str] = []
    current_start = start_offset
    current_length = 0

    def flush() -> None:
        nonlocal current_parts, current_start, current_length
        if not current_parts:
            return
        combined = "\n\n".join(current_parts)
        combined, adjusted_offset = trim_text_with_offset(combined, current_start)
        if len(combined) >= min_chars:
            chunks.append((combined, adjusted_offset))
        current_parts = []
        current_start = start_offset
        current_length = 0

    for paragraph, paragraph_offset in paragraphs:
        if len(paragraph) > max_chars:
            flush()
            for span_text, span_offset in split_long_span(paragraph, paragraph_offset, max_chars):
                if len(span_text) >= min_chars:
                    chunks.append((span_text, span_offset))
            continue

        separator = 2 if current_parts else 0
        projected_length = current_length + separator + len(paragraph)
        if current_parts and projected_length > max_chars:
            flush()

        if not current_parts:
            current_start = paragraph_offset
        current_parts.append(paragraph)
        current_length += separator + len(paragraph)
    flush()
    return chunks


def chunk_markdown_file(
    file_path: Path,
    vault_root: Path = VAULT_ROOT,
    min_chars: int = DEFAULT_MIN_CHARS,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> list[ChunkRecord]:
    raw_text = file_path.read_text(encoding="utf-8")
    relative_path = file_path.relative_to(vault_root).as_posix()
    section_type = infer_section_type(relative_path)
    document_title = extract_document_title(raw_text) or file_path.stem
    mtime = file_path.stat().st_mtime

    chunks: list[ChunkRecord] = []
    for section_title, section_text, section_offset in extract_sections(raw_text, document_title):
        for chunk_text, chunk_offset in split_section_text(section_text, section_offset, min_chars, max_chars):
            chunks.append(
                ChunkRecord(
                    file_path=relative_path,
                    section_title=section_title,
                    section_type=section_type,
                    text=chunk_text,
                    char_offset=chunk_offset,
                    file_mtime=mtime,
                )
            )
    return chunks


def build_embedding_input(chunk: ChunkRecord) -> str:
    return "\n".join(
        [
            chunk.section_type,
            chunk.file_path,
            chunk.section_title,
            chunk.text,
        ]
    )


def connect_database(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(str(Path(db_path)))
    connection.row_factory = sqlite3.Row
    return connection


def load_sqlite_vec(connection: sqlite3.Connection) -> bool:
    try:
        import sqlite_vec
    except ModuleNotFoundError:
        return False

    try:
        connection.enable_load_extension(True)
        sqlite_vec.load(connection)
        connection.enable_load_extension(False)
        return True
    except Exception:
        return False


def create_schema(connection: sqlite3.Connection, backend: str) -> bool:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY,
            file TEXT NOT NULL,
            section TEXT NOT NULL,
            type TEXT NOT NULL,
            text TEXT NOT NULL,
            char_offset INTEGER NOT NULL,
            file_mtime REAL NOT NULL
        )
        """
    )

    existing_backend = get_meta(connection, "embedding_backend")
    backend_changed = bool(existing_backend and existing_backend != backend)
    if existing_backend and existing_backend != backend:
        connection.execute("DROP TABLE IF EXISTS chunk_embeddings")

    if backend == "vec0":
        connection.execute(
            f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunk_embeddings USING vec0(
                embedding float[{DEFAULT_VECTOR_DIM}]
            )
            """
        )
    else:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chunk_embeddings (
                chunk_id INTEGER PRIMARY KEY,
                embedding BLOB NOT NULL,
                FOREIGN KEY (chunk_id) REFERENCES chunks (id) ON DELETE CASCADE
            )
            """
        )

    set_meta(connection, "embedding_backend", backend)
    set_meta(connection, "embedding_dimension", str(DEFAULT_VECTOR_DIM))
    return backend_changed


def get_meta(connection: sqlite3.Connection, key: str) -> str | None:
    row = connection.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return str(row["value"]) if row else None


def set_meta(connection: sqlite3.Connection, key: str, value: str) -> None:
    connection.execute(
        """
        INSERT INTO meta(key, value) VALUES(?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )


def clear_index(connection: sqlite3.Connection, backend: str) -> None:
    connection.execute("DELETE FROM chunks")
    if backend == "vec0":
        connection.execute("DELETE FROM chunk_embeddings")
    else:
        connection.execute("DELETE FROM chunk_embeddings")


def existing_file_mtimes(connection: sqlite3.Connection) -> dict[str, float]:
    rows = connection.execute("SELECT file, MAX(file_mtime) AS file_mtime FROM chunks GROUP BY file").fetchall()
    return {str(row["file"]): float(row["file_mtime"]) for row in rows}


def delete_chunks_for_file(connection: sqlite3.Connection, backend: str, relative_path: str) -> None:
    ids = [
        int(row["id"])
        for row in connection.execute("SELECT id FROM chunks WHERE file = ?", (relative_path,)).fetchall()
    ]
    if not ids:
        return
    if backend == "vec0":
        connection.executemany("DELETE FROM chunk_embeddings WHERE rowid = ?", ((chunk_id,) for chunk_id in ids))
    else:
        connection.executemany("DELETE FROM chunk_embeddings WHERE chunk_id = ?", ((chunk_id,) for chunk_id in ids))
    connection.execute("DELETE FROM chunks WHERE file = ?", (relative_path,))


def index_files(
    embedder: Embedder,
    vault_root: Path = VAULT_ROOT,
    db_path: str | Path = DB_PATH,
    prefer_vec: bool = True,
    force_rebuild: bool = False,
) -> dict[str, object]:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()
    with connect_database(db_path) as connection:
        backend = "vec0" if prefer_vec and load_sqlite_vec(connection) else "blob"
        backend_changed = create_schema(connection, backend)

        previous_model = get_meta(connection, "embedding_model")
        current_model = f"{embedder.model_name}:{embedder.dimension}"
        full_rebuild = force_rebuild or backend_changed or (previous_model is not None and previous_model != current_model)
        if full_rebuild:
            clear_index(connection, backend)

        disk_files = {path.relative_to(vault_root).as_posix(): path for path in collect_markdown_files(vault_root)}
        indexed_files = {} if full_rebuild else existing_file_mtimes(connection)

        removed_files = sorted(set(indexed_files) - set(disk_files))
        changed_files = sorted(
            relative_path
            for relative_path, path in disk_files.items()
            if indexed_files.get(relative_path) != path.stat().st_mtime
        )

        for relative_path in removed_files:
            delete_chunks_for_file(connection, backend, relative_path)

        chunk_records: list[ChunkRecord] = []
        for relative_path in changed_files:
            delete_chunks_for_file(connection, backend, relative_path)
            chunk_records.extend(chunk_markdown_file(disk_files[relative_path], vault_root=vault_root))

        embedding_inputs = [build_embedding_input(chunk) for chunk in chunk_records]
        embeddings = embedder.embed_documents(embedding_inputs)
        if len(embeddings) != len(chunk_records):
            raise RuntimeError("Embedder returned an unexpected number of embeddings")

        inserted_chunks = 0
        for chunk, embedding in zip(chunk_records, embeddings):
            normalized_embedding = normalize_vector(embedding)
            cursor = connection.execute(
                """
                INSERT INTO chunks(file, section, type, text, char_offset, file_mtime)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk.file_path,
                    chunk.section_title,
                    chunk.section_type,
                    chunk.text,
                    chunk.char_offset,
                    chunk.file_mtime,
                ),
            )
            chunk_id = int(cursor.lastrowid)
            serialized = serialize_vector(normalized_embedding)
            if backend == "vec0":
                connection.execute(
                    "INSERT INTO chunk_embeddings(rowid, embedding) VALUES(?, ?)",
                    (chunk_id, serialized),
                )
            else:
                connection.execute(
                    "INSERT INTO chunk_embeddings(chunk_id, embedding) VALUES(?, ?)",
                    (chunk_id, serialized),
                )
            inserted_chunks += 1

        set_meta(connection, "embedding_model", current_model)
        total_chunks = int(connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
        duration_ms = round((time.perf_counter() - started_at) * 1000, 1)
        return {
            "backend": backend,
            "changed_files": len(changed_files),
            "removed_files": len(removed_files),
            "inserted_chunks": inserted_chunks,
            "total_chunks": total_chunks,
            "db_path": str(db_path),
            "duration_ms": duration_ms,
            "model": current_model,
            "full_rebuild": full_rebuild,
        }


@dataclass
class LoadedChunk:
    chunk_id: int
    file_path: str
    section_title: str
    section_type: str
    text: str
    char_offset: int
    embedding: list[float]


class SearchIndex:
    def __init__(
        self,
        embedder: Embedder,
        db_path: str | Path = DB_PATH,
    ) -> None:
        self.db_path = Path(db_path)
        self.embedder = embedder
        self.dimension = embedder.dimension
        self.backend = "blob"
        self.chunks: list[LoadedChunk] = []
        self.reload()

    def reload(self) -> None:
        if not self.db_path.exists():
            raise SearchConfigurationError(
                f"Search database not found at {self.db_path}. Run `python tools/search/index.py` first."
            )

        with connect_database(self.db_path) as connection:
            self.backend = get_meta(connection, "embedding_backend") or "blob"
            chunk_count = int(connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
            rows = self._fetch_rows(connection)
            if chunk_count != len(rows):
                raise SearchConfigurationError(
                    "Search index is inconsistent. Run `python tools/search/index.py --rebuild` to rebuild it."
                )
            self.chunks = [self._row_to_chunk(row) for row in rows]

    def _fetch_rows(self, connection: sqlite3.Connection) -> list[sqlite3.Row]:
        if self.backend == "vec0":
            try:
                load_sqlite_vec(connection)
            except Exception:
                pass
            return connection.execute(
                """
                SELECT
                    c.id,
                    c.file,
                    c.section,
                    c.type,
                    c.text,
                    c.char_offset,
                    e.embedding
                FROM chunks AS c
                JOIN chunk_embeddings AS e
                    ON e.rowid = c.id
                ORDER BY c.id
                """
            ).fetchall()
        return connection.execute(
            """
            SELECT
                c.id,
                c.file,
                c.section,
                c.type,
                c.text,
                c.char_offset,
                e.embedding
            FROM chunks AS c
            JOIN chunk_embeddings AS e
                ON e.chunk_id = c.id
            ORDER BY c.id
            """
        ).fetchall()

    def _row_to_chunk(self, row: sqlite3.Row) -> LoadedChunk:
        return LoadedChunk(
            chunk_id=int(row["id"]),
            file_path=str(row["file"]),
            section_title=str(row["section"]),
            section_type=str(row["type"]),
            text=str(row["text"]),
            char_offset=int(row["char_offset"]),
            embedding=deserialize_vector(bytes(row["embedding"]), self.dimension),
        )

    @lru_cache(maxsize=128)
    def _embed_query_cached(self, query: str) -> tuple[float, ...]:
        return tuple(self.embedder.embed_query(query))

    def search(self, query: str, filters: Sequence[str] | None = None, top_k: int = DEFAULT_TOP_K) -> dict[str, object]:
        cleaned_query = query.strip()
        if not cleaned_query:
            return {"mode": "semantic", "results": [], "total": 0}

        selected_filters = set(filters or ALLOWED_FILTERS) & ALLOWED_FILTERS
        if not selected_filters:
            selected_filters = set(ALLOWED_FILTERS)

        semantic_results = self._semantic_search(cleaned_query, selected_filters, top_k)
        if semantic_results and semantic_results[0].score is not None and semantic_results[0].score >= SEMANTIC_SCORE_THRESHOLD:
            return {
                "mode": "semantic",
                "results": [result.as_dict() for result in semantic_results],
                "total": len(semantic_results),
            }

        keyword_results = self._keyword_search(cleaned_query, selected_filters, top_k)
        if keyword_results:
            return {
                "mode": "keyword",
                "results": [result.as_dict() for result in keyword_results],
                "total": len(keyword_results),
            }

        return {
            "mode": "semantic",
            "results": [result.as_dict() for result in semantic_results],
            "total": len(semantic_results),
        }

    def _semantic_search(self, query: str, filters: set[str], top_k: int) -> list[SearchResult]:
        query_embedding = self._embed_query_cached(query)
        scored: list[tuple[float, LoadedChunk]] = []
        for chunk in self.chunks:
            if chunk.section_type not in filters:
                continue
            score = cosine_similarity(query_embedding, chunk.embedding)
            scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            SearchResult(
                file_path=chunk.file_path,
                section_title=chunk.section_title,
                section_type=chunk.section_type,
                snippet=build_snippet(chunk.text, query),
                score=round(score, 4),
                match_type="semantic",
                char_offset=chunk.char_offset,
            )
            for score, chunk in scored[:top_k]
        ]

    def _keyword_search(self, query: str, filters: set[str], top_k: int) -> list[SearchResult]:
        query_lower = query.lower()
        query_terms = [term for term in tokenize(query_lower) if len(term) >= 2]
        scored: list[tuple[int, LoadedChunk]] = []
        for chunk in self.chunks:
            if chunk.section_type not in filters:
                continue
            haystack = " \n".join([chunk.file_path, chunk.section_title, chunk.text]).lower()
            score = 0
            if query_lower in haystack:
                score += 12
            for term in query_terms:
                score += haystack.count(term)
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda item: (item[0], item[1].file_path, item[1].section_title), reverse=True)
        return [
            SearchResult(
                file_path=chunk.file_path,
                section_title=chunk.section_title,
                section_type=chunk.section_type,
                snippet=build_snippet(chunk.text, query),
                score=None,
                match_type="keyword",
                char_offset=chunk.char_offset,
            )
            for _, chunk in scored[:top_k]
        ]


def build_snippet(text: str, query: str, limit: int = 220) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= limit:
        return collapsed

    candidates = [query.strip().lower(), *[term.lower() for term in tokenize(query) if len(term) >= 3]]
    index = -1
    for candidate in candidates:
        if not candidate:
            continue
        index = collapsed.lower().find(candidate)
        if index != -1:
            break

    if index == -1:
        snippet = collapsed[: limit - 1].rstrip()
        return f"{snippet}..."

    half_window = limit // 2
    start = max(0, index - half_window)
    end = min(len(collapsed), start + limit)
    start = max(0, end - limit)
    snippet = collapsed[start:end].strip()
    if start > 0:
        snippet = f"...{snippet}"
    if end < len(collapsed):
        snippet = f"{snippet}..."
    return snippet


def build_index_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build or refresh the local semantic search index.")
    parser.add_argument(
        "--embedder",
        choices=["sentence-transformer", "hash"],
        default=os.environ.get("SEARCH_EMBEDDER", "sentence-transformer"),
        help="Embedding backend to use while indexing.",
    )
    parser.add_argument(
        "--db",
        default=str(DB_PATH),
        help="Path to the SQLite database file.",
    )
    parser.add_argument(
        "--vault",
        default=str(VAULT_ROOT),
        help="Path to the Obsidian vault root.",
    )
    parser.add_argument(
        "--disable-sqlite-vec",
        action="store_true",
        help="Store embeddings in a plain SQLite table instead of the sqlite-vec virtual table.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Clear existing indexed data and rebuild all chunks from scratch.",
    )
    return parser
