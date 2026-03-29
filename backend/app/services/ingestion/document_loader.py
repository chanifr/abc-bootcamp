"""Document loading — converts PDF, DOCX, or plain-text files to raw strings.

This stage does no interpretation; it only produces text for downstream stages.
"""
from pathlib import Path


class DocumentLoadError(Exception):
    """Raised when a file cannot be read or produces empty text."""


def load_document(path: Path) -> tuple[str, str]:
    """Load *path* and return ``(raw_text, parser_name)``.

    Raises ``DocumentLoadError`` on unrecognised extensions or empty output.
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _load_pdf(path)
    elif suffix in (".docx", ".doc"):
        return _load_docx(path)
    elif suffix in (".txt", ".text", ""):
        return _load_text(path)
    else:
        raise DocumentLoadError(f"Unsupported file type: {suffix!r} ({path.name})")


def _load_pdf(path: Path) -> tuple[str, str]:
    try:
        import pdfplumber
    except ImportError as exc:
        raise DocumentLoadError("pdfplumber is not installed") from exc

    try:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
    except Exception as exc:
        raise DocumentLoadError(f"Failed to open PDF {path.name}: {exc}") from exc

    text = "\n".join(pages).strip()
    if not text:
        raise DocumentLoadError(
            f"PDF produced no extractable text (possibly scanned/image-only): {path.name}"
        )
    return text, "pdfplumber"


def _load_docx(path: Path) -> tuple[str, str]:
    try:
        from docx import Document
    except ImportError as exc:
        raise DocumentLoadError("python-docx is not installed") from exc

    try:
        doc = Document(str(path))
    except Exception as exc:
        raise DocumentLoadError(f"Failed to open DOCX {path.name}: {exc}") from exc

    text = "\n".join(para.text for para in doc.paragraphs).strip()
    if not text:
        raise DocumentLoadError(f"DOCX produced no text: {path.name}")
    return text, "python-docx"


def _load_text(path: Path) -> tuple[str, str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        raise DocumentLoadError(f"Failed to read text file {path.name}: {exc}") from exc

    if not text:
        raise DocumentLoadError(f"Text file is empty: {path.name}")
    return text, "plaintext"
