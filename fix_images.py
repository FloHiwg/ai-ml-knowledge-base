#!/usr/bin/env python3
"""
Fix image references in downloaded Markdown articles.

When articles are saved locally, images end up referenced as:
  ![](FolderName/https%253A%252F%252F...ext)

where the folder exists as a sibling directory containing the actual image files
named with single-encoded URLs (e.g. https%3A%2F%2F...jpeg).

This script rewrites those references to point to the correct local files,
fixing both the folder encoding and the file extension.

Usage:
  python fix_images.py <file.md>          # fix a single file
  python fix_images.py <directory>        # fix all .md files in a directory
"""

import os
import re
import sys
import urllib.parse


def build_id_map(folder_path: str) -> dict[str, str]:
    """Map image_id -> actual filename for all files in the local image folder."""
    id_map = {}
    for filename in os.listdir(folder_path):
        decoded = urllib.parse.unquote(filename)
        basename = decoded.split("/")[-1]
        image_id = os.path.splitext(basename)[0]
        id_map[image_id] = filename
    return id_map


def fix_file(md_path: str) -> int:
    """Fix image references in a single markdown file. Returns number of fixes made."""
    folder_name = os.path.splitext(os.path.basename(md_path))[0]
    folder_path = os.path.join(os.path.dirname(md_path), folder_name)

    if not os.path.isdir(folder_path):
        print(f"  Skipping: no image folder found at '{folder_path}'")
        return 0

    id_map = build_id_map(folder_path)
    if not id_map:
        print(f"  Skipping: image folder is empty")
        return 0

    with open(md_path, "r") as f:
        content = f.read()

    fixes = 0

    def replace_image(match: re.Match) -> str:
        nonlocal fixes
        alt_text = match.group(1)
        raw_path = match.group(2)

        # Strip the folder prefix (everything up to and including the first '/')
        if "/" not in raw_path:
            return match.group(0)
        encoded_file = raw_path.split("/", 1)[1]

        # Double-decode to recover the original URL, then extract the image ID
        decoded_url = urllib.parse.unquote(urllib.parse.unquote(encoded_file))
        basename = decoded_url.split("/")[-1]
        image_id = os.path.splitext(basename)[0]

        if image_id not in id_map:
            print(f"  No local file for: {image_id}")
            return match.group(0)

        local_file = id_map[image_id]
        rel_path = urllib.parse.quote(folder_name) + "/" + urllib.parse.quote(local_file)
        fixes += 1
        return f"![{alt_text}]({rel_path})"

    # Match ![alt](path) where path starts with the (possibly encoded) folder name
    # Handle both encoded and unencoded parentheses in the folder name
    encoded_folder = re.escape(urllib.parse.quote(folder_name, safe="()"))
    encoded_folder_strict = re.escape(urllib.parse.quote(folder_name))
    pattern = re.compile(
        rf"!\[([^\]]*)\]\((?:{encoded_folder}|{encoded_folder_strict})/([^)]*)\)"
    )

    new_content = pattern.sub(replace_image, content)

    if fixes:
        with open(md_path, "w") as f:
            f.write(new_content)

    return fixes


def process(path: str):
    if os.path.isfile(path):
        if not path.endswith(".md"):
            print(f"Not a markdown file: {path}")
            return
        n = fix_file(path)
        print(f"{os.path.basename(path)}: {n} image(s) fixed")
    elif os.path.isdir(path):
        md_files = [f for f in os.listdir(path) if f.endswith(".md")]
        if not md_files:
            print(f"No .md files found in {path}")
            return
        for filename in sorted(md_files):
            md_path = os.path.join(path, filename)
            n = fix_file(md_path)
            print(f"{filename}: {n} image(s) fixed")
    else:
        print(f"Path not found: {path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_images.py <file.md or directory>")
        sys.exit(1)
    process(sys.argv[1])
