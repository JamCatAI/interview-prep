"""Load job posting and CV from files, URLs, or raw text."""
import os
import re
import subprocess
import sys


def load_text(source: str) -> str:
    """Load text from a file path, URL, or raw string."""
    if os.path.isfile(source):
        with open(source, "rb") as f:
            raw = f.read()
        # try PDF
        if source.lower().endswith(".pdf") or raw[:4] == b"%PDF":
            return _pdf_to_text(source)
        return raw.decode("utf-8", errors="replace")

    if source.startswith("http://") or source.startswith("https://"):
        return _fetch_url(source)

    return source  # treat as raw text


def _pdf_to_text(path: str) -> str:
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", path, "-"],
            capture_output=True, text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except FileNotFoundError:
        pass
    # fallback: pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        print("error: install pypdf to read PDFs  (pip install pypdf)", file=sys.stderr)
        sys.exit(1)


def _fetch_url(url: str) -> str:
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        return _strip_html(html)
    except Exception as e:
        print(f"error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)


def _strip_html(html: str) -> str:
    # remove scripts/styles
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # remove tags
    text = re.sub(r"<[^>]+>", " ", html)
    # collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
