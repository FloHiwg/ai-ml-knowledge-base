# Search Interface PRD

**Status:** Draft  
**Scope:** Local semantic search over this knowledge base vault  

---

## Problem

Obsidian's built-in keyword search is string-matching only. Searching for "alignment training" won't surface a note that talks about "RLHF and preference optimization." The knowledge base is concept-dense and cross-linked — it needs semantic retrieval to be useful.

---

## Goal

A locally-running web app that lets me search the vault by meaning, not keywords, and jump directly into Obsidian from the results.

---

## Users

One user: me. Runs locally, no auth, no multi-tenancy.

---

## Use Cases

1. **Concept recall** — "what did I read about cosine similarity as a reward signal?" → surfaces the RLSR summary without needing to remember the paper title.
2. **Cross-document synthesis** — "what do I know about catastrophic forgetting?" → pulls relevant fragments from wiki, summaries, and manual notes together.
3. **Pre-writing check** — before writing a new wiki page, search to find what already exists on the topic.
4. **Navigation shortcut** — faster than browsing the vault tree to land on a specific page.

---

## Functional Requirements

### Search

- **Semantic query**: free-text query, embedded and matched against pre-indexed document chunks
- **Keyword fallback**: if no strong semantic hits, surface exact-match results
- **Instant results**: results appear as-you-type after a short debounce (~300ms), or on Enter
- **Result card shows**:
  - File path (relative to vault root), shown with section type as a tag (`wiki`, `summary`, `manual`, `raw`)
  - Matched chunk text (~200 chars of context around the best-matching passage)
  - Cosine similarity score (shown as a subtle percentage or omitted from display but used for ranking)
- **Top N results**: show top 10 by default; no pagination needed at this scale

### Filtering

- Filter by section type: `wiki` / `summaries` / `manual` (checkboxes, all on by default)
- No date or tag filtering needed for MVP

### Navigation

- Each result card has an **"Open in Obsidian"** button/link using the URI:
  ```
  obsidian://open?vault=knowledge-base&file=<relative-path-without-extension>
  ```
- Clicking the card title also opens Obsidian
- Keyboard: `↑`/`↓` to navigate results, `Enter` to open top result in Obsidian

### Indexing

- **Triggered manually** or on startup: a script re-indexes all `.md` files
- Index stored in `search.db` (SQLite + sqlite-vec) — no external services
- Re-index takes <5s for the current vault size
- Files excluded from indexing: `raw/` (PDFs and article sources are already summarized)

---

## Technical Design

### Stack

| Component | Choice | Rationale |
|---|---|---|
| Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` | 80MB, runs CPU-only, 384-dim, fast |
| Vector store | SQLite (`sqlite-vec` extension) + cosine similarity | Single file, queryable, inspectable |
| Backend | `FastAPI` with a single `/search` endpoint | Minimal, easy to extend |
| Frontend | Single `index.html` + vanilla JS | No build toolchain; easy to modify |
| Persistence | `search.db` — single SQLite file | Portable, no dependencies, gitignored |

### Chunking Strategy

- Chunk at the **section level** (split on `##` headings)
- Each chunk carries metadata: `file_path`, `section_title`, `section_type` (wiki/summary/manual), `char_offset`
- Min chunk size: 100 chars (skip stubs); max: 800 chars (split long sections at paragraph boundaries)
- Overlap: none (sections are already semantically coherent in this vault)

### Database Schema

Single SQLite file (`search.db`) with the `sqlite-vec` extension for vector operations.

```sql
CREATE TABLE chunks (
    id          INTEGER PRIMARY KEY,
    file        TEXT NOT NULL,       -- e.g. "wiki/training/fine-tuning.md"
    section     TEXT NOT NULL,       -- e.g. "DPO — Direct Preference Optimization"
    type        TEXT NOT NULL,       -- "wiki" | "summary" | "manual"
    text        TEXT NOT NULL,       -- raw chunk text
    file_mtime  REAL NOT NULL        -- used to detect stale chunks on re-index
);

CREATE VIRTUAL TABLE chunk_embeddings USING vec0(
    chunk_id INTEGER PRIMARY KEY,
    embedding FLOAT[384]             -- all-MiniLM-L6-v2 output dimension
);
```

`sqlite-vec` ships as a single `.so` / `.dylib` loadable extension — no separate server, no install beyond `pip install sqlite-vec`. On re-index, stale chunks (file mtime changed) are deleted and reinserted.

On startup, the server loads all embeddings into a `numpy` array in memory for fast batch cosine similarity; SQLite is the source of truth and handles persistence.

### Query Flow

```
User types query
  → debounce 300ms
  → POST /search {query, filters, top_k}
  → embed query (cached if repeated)
  → cosine similarity against all chunk embeddings
  → return top_k results with score + metadata
  → render result cards
```

### Deep Link Format

```
obsidian://open?vault=knowledge-base&file=wiki/training/fine-tuning
```

File path must be relative to vault root, no `.md` extension.

---

## File Layout

```
tools/
  search/
    index.py          # build/rebuild the search index
    server.py         # FastAPI app
    static/
      index.html      # search UI
    search.db         # generated, gitignored
```

---

## UI Design

Minimal, functional. Roughly:

```
┌─────────────────────────────────────────────┐
│  🔍  [search query input                   ] │
│       [ ] wiki  [ ] summaries  [ ] manual    │
├─────────────────────────────────────────────┤
│  fine-tuning.md · wiki                  92%  │
│  DPO — Direct Preference Optimization        │
│  The optimal policy under the RLHF           │
│  objective can be expressed analytically...  │
│                          [Open in Obsidian]  │
├─────────────────────────────────────────────┤
│  RLSR.md · summary                      87%  │
│  ...                                         │
└─────────────────────────────────────────────┘
```

- Dark background to match Obsidian
- Monospace font for file paths, sans-serif for text
- No logo, no header chrome — just search box + results

---

## Out of Scope (MVP)

- Hybrid BM25 + semantic reranking
- Incremental indexing (watch filesystem for changes)
- Search history or saved queries
- Indexing raw PDF content directly (summaries cover this)
- Auth or network exposure
- Mobile layout

---

## Success Criteria

- Finding a concept I've read about takes <15 seconds from opening the interface
- "Open in Obsidian" lands on the correct file every time
- Re-indexing after adding new articles takes <10 seconds
- No external API calls — fully offline

---

## Decisions

1. **Re-index trigger**: `python index.py` — manual CLI only, no UI button needed.
2. **Startup**: `python server.py` — manual, no launchd.
3. **Vault name**: hardcoded to `knowledge-base` in deep links.
