# ai-ml-knowledge-base

A personal knowledge base about AI/ML topics, inspired by [Andrej Karpathy's approach](https://x.com/karpathy/status/2039805659525644595) to LLM-assisted knowledge management.

## Concept

The idea is to collect raw sources (articles, papers, etc.) and use LLMs - primarily Claude Code - to incrementally compile and maintain a structured wiki from them. The pattern:

- **`knowledge-base/raw/`** — source documents as ingested markdown
- **`knowledge-base/summaries/`** — LLM-generated summaries of raw articles
- **`knowledge-base/wiki/`** — LLM-compiled wiki: concept articles, cross-links, and index files
- **`knowledge-base/manual/`** — hand-written notes and cheat sheets that I was maintaining beforehand already

The wiki is maintained by the LLM, not edited by hand. New raw sources get "compiled" into it incrementally — summaries written, concepts updated, backlinks added.

## Collection Workflow

Articles and other sources are clipped from the web as markdown using [MarkSnip](https://marksnip.com/), which also downloads all images locally alongside the document. After clipping, image references in the markdown are often broken due to URL encoding issues — `fix_images.py` fixes those paths so images render correctly in Obsidian.

Obsidian is used as the reading and browsing frontend for both raw sources and the compiled wiki.

## Goal

I've been collecting and hoarding information about topics I care about for a while. This repo is an attempt to make that habit more structured and maintainable. LLMs (especially Claude Code) handle the organization, synthesis, and upkeep — so I can focus on feeding in sources and asking questions.

Eventually: Q&A against the wiki, linting for inconsistencies, and generating outputs (slides, visualizations) — all viewable in Obsidian.

## TODO / Things to explore

### Ingest
- [x] Clip web articles as local markdown with images downloaded alongside
- [x] Fix broken image references so the local markdown renders correctly

### Wiki compilation
- [ ] Establish a repeatable LLM workflow to incrementally compile raw sources into the wiki (summaries, concept articles, backlinks)
- [ ] Auto-maintain an index and brief per-document summaries to support Q&A without needing retrieval infrastructure

### Q&A
- [ ] Test complex multi-document questions against the wiki once it reaches meaningful size
- [ ] Evaluate whether the LLM can navigate the wiki well via index files alone vs. needing a dedicated search tool

### Output
- [ ] Have query outputs rendered as markdown and filed back into the wiki so explorations accumulate
- [ ] Try other output formats (slides, visualizations) viewable directly in the knowledge base

### Linting / health checks
- [ ] Run LLM health checks to surface inconsistent or conflicting information across articles
- [ ] Impute missing data in incomplete articles using web search
- [ ] Generate suggestions for new article candidates based on gaps and unexplored connections

### Tooling
- [x] Build a lightweight search interface over the wiki, usable both directly and as a tool handed off to an LLM

## Search Interface

A local semantic search app lives under `tools/search/`. It indexes the wiki, summaries, and manual notes using sentence embeddings, stores them in SQLite, and serves a web UI with deep links back into Obsidian.

### Setup

**1. Install dependencies** (Python 3.10+ required)

```bash
pip install -r tools/search/requirements.txt
```

**2. Build the index**

```bash
python3 tools/search/index.py
```

Chunks all `.md` files in `wiki/`, `summaries/`, and `manual/` by section, embeds them with `all-MiniLM-L6-v2`, and writes to `tools/search/search.db`. First run takes ~10s; subsequent runs only re-embed changed files.

To force a full rebuild:

```bash
python3 tools/search/index.py --rebuild
```

**3. Start the server**

```bash
python3 tools/search/server.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Results link directly into Obsidian via `obsidian://` deep links — make sure the vault is open in Obsidian first.

### Notes

- `search.db` is gitignored — regenerate locally after cloning
- The model (~80MB) downloads automatically on first run and is cached in `~/.cache/huggingface/`
- To re-index on server startup: `SEARCH_REINDEX_ON_STARTUP=1 python3 tools/search/server.py`

### Future
- [ ] Explore synthetic data generation + fine-tuning so the LLM "knows" the knowledge base in its weights rather than just its context
