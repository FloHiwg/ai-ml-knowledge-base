# Search Tool

Local semantic search for the Obsidian vault.

## Install

```bash
python3 -m pip install -r tools/search/requirements.txt
```

## Index the vault

```bash
python3 tools/search/index.py
```

For a dependency-light local fallback while testing, use:

```bash
python3 tools/search/index.py --embedder hash --disable-sqlite-vec
```

To fully rebuild the index from scratch:

```bash
python3 tools/search/index.py --rebuild
```

## Start the server

```bash
python3 tools/search/server.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Optional startup reindex

```bash
SEARCH_REINDEX_ON_STARTUP=1 python3 tools/search/server.py
```
