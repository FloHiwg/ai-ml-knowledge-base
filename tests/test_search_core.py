from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.search.search_core import HashingEmbedder, SearchIndex, chunk_markdown_file, index_files


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class SearchCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.vault = self.root / "knowledge-base"

        write_file(
            self.vault / "wiki/training/fine-tuning.md",
            """# Fine-Tuning

## DPO

Direct preference optimization is a post-training method related to RLHF and preference data.
It replaces a separate reward model with a direct objective over chosen and rejected completions,
which makes alignment simpler to train while still capturing the idea of human preference learning.

## Catastrophic Forgetting

Parameter-efficient tuning methods such as LoRA help reduce catastrophic forgetting when adapting
to a new task. The main idea is that you preserve prior capabilities by updating fewer parameters
instead of rewriting the whole model when the target task is narrow and domain-specific.
""",
        )
        write_file(
            self.vault / "summaries/RLSR.md",
            """# RLSR

## Reward Signal

Cosine similarity can be used as a reward signal for representation learning and retrieval setups.
This comes up when comparing latent vectors, measuring alignment between model states, and scoring
how close a generated representation is to a desired target in an embedding space.
""",
        )
        write_file(
            self.vault / "manual/Notes.md",
            """# Notes

## Search

This note explains a local search interface for the vault with Obsidian deep links.
The interface should support semantic retrieval, exact-match fallback behavior, and a direct way
to open the underlying note in Obsidian without browsing the file tree manually.
""",
        )

        self.db_path = self.root / "search.db"
        self.embedder = HashingEmbedder()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_chunk_markdown_file_splits_by_sections(self) -> None:
        chunks = chunk_markdown_file(self.vault / "wiki/training/fine-tuning.md", vault_root=self.vault)
        sections = [chunk.section_title for chunk in chunks]
        self.assertIn("DPO", sections)
        self.assertIn("Catastrophic Forgetting", sections)

    def test_index_and_semantic_search(self) -> None:
        index_files(
            embedder=self.embedder,
            vault_root=self.vault,
            db_path=self.db_path,
            prefer_vec=False,
        )
        search = SearchIndex(embedder=self.embedder, db_path=self.db_path)
        payload = search.search(
            "direct preference optimization RLHF chosen rejected completions",
            filters=["wiki"],
            top_k=5,
        )

        self.assertEqual(payload["mode"], "semantic")
        self.assertGreaterEqual(payload["total"], 1)
        first = payload["results"][0]
        self.assertEqual(first["section_title"], "DPO")
        self.assertIn("obsidian://open", first["obsidian_url"])

    def test_keyword_fallback(self) -> None:
        index_files(
            embedder=self.embedder,
            vault_root=self.vault,
            db_path=self.db_path,
            prefer_vec=False,
        )
        search = SearchIndex(embedder=self.embedder, db_path=self.db_path)
        payload = search.search("deep links", filters=["manual"], top_k=5)

        self.assertEqual(payload["mode"], "keyword")
        self.assertEqual(payload["results"][0]["file_path"], "manual/Notes.md")


if __name__ == "__main__":
    unittest.main()
