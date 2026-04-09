from __future__ import annotations

import json
from pathlib import Path

from search_core import build_index_parser, get_embedder, index_files


def main() -> None:
    parser = build_index_parser()
    args = parser.parse_args()

    stats = index_files(
        embedder=get_embedder(args.embedder),
        vault_root=Path(args.vault),
        db_path=Path(args.db),
        prefer_vec=not args.disable_sqlite_vec,
        force_rebuild=args.rebuild,
    )
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
