# Search Tool

Local semantic search for the Obsidian vault.

## Setup

Create a virtual environment and install dependencies using [uv](https://github.com/astral-sh/uv):

```bash
cd tools/search
uv venv .venv
uv pip install -r requirements.txt
```

All subsequent commands use the venv's Python. From the **repo root**:

```bash
tools/search/.venv/bin/python tools/search/index.py --rebuild
tools/search/.venv/bin/python tools/search/server.py
```

Or activate the venv first:

```bash
source tools/search/.venv/bin/activate
```

## Index the vault

```bash
python tools/search/index.py
```

For a dependency-light local fallback while testing, use:

```bash
python tools/search/index.py --embedder hash --disable-sqlite-vec
```

To fully rebuild the index from scratch:

```bash
python tools/search/index.py --rebuild
```

## Start the server

```bash
python tools/search/server.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Optional startup reindex

```bash
SEARCH_REINDEX_ON_STARTUP=1 python tools/search/server.py
```
