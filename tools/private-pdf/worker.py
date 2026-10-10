"""Networkless container worker. Input and output are bounded UTF-8/byte streams."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys

MAX_INPUT = 50 * 1024 * 1024
MAX_TEXT = 32 * 1024 * 1024
MAX_PAGES = 1000


def run(args):
    result = subprocess.run(
        args, capture_output=True, timeout=60, check=True,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "TZ": "UTC"},
    )
    # Poppler warnings can signal a repaired, damaged or ambiguous document.
    if result.stderr:
        raise ValueError("PDF parser emitted diagnostics; manual investigation required")
    return result.stdout.decode("utf-8", errors="strict")


def main():
    os.umask(0o077)
    data = sys.stdin.buffer.read(MAX_INPUT + 1)
    if len(data) > MAX_INPUT or not data.startswith(b"%PDF-"):
        raise ValueError("Invalid or oversized PDF")
    pdf = Path("/tmp/source.pdf")
    pdf.write_bytes(data)
    info = run(["pdfinfo", str(pdf)])
    match = re.search(r"^Pages:\s+(\d+)\s*$", info, re.MULTILINE)
    if not match or not 0 < int(match[1]) <= MAX_PAGES:
        raise ValueError("Missing or excessive PDF page count")
    if not re.search(r"^Encrypted:\s+no\s*$", info, re.MULTILINE):
        raise ValueError("Encrypted PDF is not supported")
    text_file = Path("/tmp/pages.txt")
    run(["pdftotext", "-layout", "-enc", "UTF-8", "-eol", "unix", str(pdf), str(text_file)])
    if text_file.stat().st_size > MAX_TEXT:
        raise ValueError("Extracted text exceeds limit")
    text = text_file.read_text(encoding="utf-8")
    # One terminal form feed per physical page, including empty pages.
    parts = text.split("\f")
    if parts[-1] != "" or len(parts) - 1 != int(match[1]):
        raise ValueError("Text delimiters do not match PDF page count")
    version = subprocess.run(
        ["pdftotext", "-v"], capture_output=True, check=True, timeout=5,
    ).stderr.decode("utf-8").splitlines()[0]
    json.dump({"page_count": int(match[1]), "pages": parts[:-1], "extractor": version}, sys.stdout,
              ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Do not echo source text or arbitrary parser diagnostics into host logs.
        print("Private PDF extraction failed", file=sys.stderr)
        sys.exit(1)
