#!/usr/bin/env python3
"""Build PDF from RST book sources via pandoc (RST→Typst) and typst compile."""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TYPST_TEMPLATE = PROJECT_ROOT / "typst" / "template.typ"
FONTS_DIR = PROJECT_ROOT / "fonts"

# RST heading underline characters ordered by level.
# When we normalize, level 0 uses HEADING_CHARS[0], etc.
HEADING_CHARS = "#*=-~^"

# Regex to detect RST headings. Matches:
#   optional overline (same char repeated 3+)
#   title line
#   underline (same char repeated 3+)
HEADING_RE = re.compile(
    r"^(?P<overline>(?P<ochar>[^\w\s])\2{2,}\n)?"
    r"(?P<title>.+)\n"
    r"(?P<underline>(?P<uchar>[^\w\s])\5{2,})$",
    re.MULTILINE,
)

# Regex to detect toctree directives and their content
TOCTREE_RE = re.compile(
    r"^\.\. toctree::.*\n(?:[ \t]+:.*\n)*(?:\n(?:[ \t]+\S.*\n)*)?",
    re.MULTILINE,
)

# Regex to detect :doc: roles
# Matches :doc:`display text <target>` or :doc:`target`
DOC_ROLE_RE = re.compile(r":doc:`(?:([^<`]+?)\s*<[^>]+>|([^`]+))`")

# Regex for :layout: field list
LAYOUT_RE = re.compile(r"^:layout:.*\n", re.MULTILINE)


def parse_toctree(index_path: Path, book_dir: Path) -> list[tuple[Path, int]]:
    """Recursively walk toctree from index_path, returning (filepath, depth) tuples."""
    result = []
    _walk_toctree(index_path, book_dir, 0, result)
    return result


def _walk_toctree(rst_path: Path, book_dir: Path, depth: int, result: list):
    """Recursive helper for toctree walking."""
    result.append((rst_path, depth))
    content = rst_path.read_text(encoding="utf-8")

    for match in re.finditer(
        r"\.\. toctree::.*\n(?:[ \t]+:.*\n)*\n?((?:[ \t]+\S.*\n)*)", content
    ):
        entries_block = match.group(1)
        for line in entries_block.strip().splitlines():
            entry = line.strip()
            if not entry:
                continue
            child_path = book_dir / (entry + ".rst")
            if child_path.exists():
                _walk_toctree(child_path, book_dir, depth + 1, result)


def preprocess_rst(content: str) -> str:
    """Strip Sphinx-specific directives from RST content."""
    # Remove toctree directives
    content = TOCTREE_RE.sub("", content)
    # Convert :doc: roles to italic text
    content = DOC_ROLE_RE.sub(lambda m: f"*{m.group(1) or m.group(2)}*", content)
    # Remove :layout: field lists
    content = LAYOUT_RE.sub("", content)
    return content


def _find_headings(content: str) -> list[dict]:
    """Find all headings in RST content with their positions and levels."""
    headings = []
    # Track which underline chars we've seen to determine relative levels
    char_order = []

    for match in HEADING_RE.finditer(content):
        uchar = match.group("uchar")
        has_overline = match.group("overline") is not None

        # Build a key that distinguishes overlined vs underlined-only headings
        key = (uchar, has_overline)
        if key not in char_order:
            char_order.append(key)

        local_level = char_order.index(key)
        headings.append(
            {
                "match": match,
                "local_level": local_level,
                "title": match.group("title"),
                "has_overline": has_overline,
            }
        )
    return headings


def normalize_headings(content: str, depth_offset: int) -> str:
    """Shift heading levels based on toctree depth."""
    headings = _find_headings(content)
    if not headings:
        return content

    # Process in reverse order to preserve positions
    for heading in reversed(headings):
        match = heading["match"]
        target_level = heading["local_level"] + depth_offset
        target_level = min(target_level, len(HEADING_CHARS) - 1)
        char = HEADING_CHARS[target_level]
        title = heading["title"]
        title_len = max(len(title), 3)
        underline = char * title_len

        # Always use underline-only style so that all headings at the
        # same target level use the same RST convention — pandoc determines
        # heading depth by first-seen (char, style) pair, so mixing
        # overlined and underline-only with the same char creates two
        # separate levels.
        replacement = f"{title}\n{underline}"

        content = content[: match.start()] + replacement + content[match.end() :]

    return content


def postprocess_typst(content: str) -> str:
    """Fix known issues in pandoc-generated Typst output."""
    # Fix px units -> pt (Typst doesn't support px)
    content = re.sub(r"(\d+)px", r"\1pt", content)
    # Fix escaped quotes that pandoc generates — replace \' with '
    content = content.replace("\\'", "'")
    # Escape / at start of lines to prevent Typst term list interpretation
    content = re.sub(r"^/ ", r"\/\ ", content, flags=re.MULTILINE)
    return content


def build_book(
    book_dir: Path, title: str, author: str, output_path: Path
) -> None:
    """Build a PDF for a single book."""
    index_path = book_dir / "index.rst"
    if not index_path.exists():
        print(f"Error: {index_path} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Building PDF for: {book_dir.name}")

    # Collect files in toctree order
    files = parse_toctree(index_path, book_dir)
    print(f"  Found {len(files)} RST files")

    # Preprocess and concatenate
    # The index file (depth 0) provides the book title which is already
    # passed via --variable title, so we strip its headings to avoid a
    # duplicate title and to let part headings become the top-level (L1)
    # headings in the PDF.  All other files use (depth - 1) as offset so
    # parts map to L1 and chapters to L2.
    parts = []
    for filepath, depth in files:
        content = filepath.read_text(encoding="utf-8")
        content = preprocess_rst(content)
        if depth == 0:
            # Strip all headings from the root index file
            content = HEADING_RE.sub(lambda m: "", content)
        else:
            content = normalize_headings(content, depth - 1)
        parts.append(content)

    combined_rst = "\n\n".join(parts)

    # Write combined RST to temp file (in book_dir so relative image paths work)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".rst",
        dir=book_dir,
        delete=False,
        encoding="utf-8",
    ) as rst_file:
        rst_file.write(combined_rst)
        rst_tmp = Path(rst_file.name)

    typst_tmp = rst_tmp.with_suffix(".typ")

    try:
        # Run pandoc: RST -> Typst
        pandoc_cmd = [
            "pandoc",
            "--from", "rst",
            "--to", "typst",
            "--template", str(TYPST_TEMPLATE),
            "--variable", f"title={title}",
            "--variable", f"author={author}",
            "-o", str(typst_tmp),
            str(rst_tmp),
        ]
        print(f"  Running pandoc...")
        subprocess.run(pandoc_cmd, check=True, cwd=book_dir)

        # Post-process generated Typst
        typst_content = typst_tmp.read_text(encoding="utf-8")
        typst_content = postprocess_typst(typst_content)
        typst_tmp.write_text(typst_content, encoding="utf-8")

        # Run typst compile
        typst_cmd = [
            "typst", "compile",
            "--font-path", str(FONTS_DIR),
            str(typst_tmp),
            str(output_path),
        ]
        print(f"  Running typst compile...")
        subprocess.run(typst_cmd, check=True, cwd=book_dir)

        print(f"  Output: {output_path}")
    finally:
        rst_tmp.unlink(missing_ok=True)
        typst_tmp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Build PDF from RST book sources")
    parser.add_argument("book_dir", help="Book directory (relative to project root)")
    parser.add_argument("--title", required=True, help="Book title")
    parser.add_argument("--author", default="", help="Book author")
    parser.add_argument("--output", required=True, help="Output PDF path")
    args = parser.parse_args()

    book_dir = PROJECT_ROOT / args.book_dir
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    build_book(book_dir, args.title, args.author, output_path)


if __name__ == "__main__":
    main()
