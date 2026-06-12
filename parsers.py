import pathlib


def read_document(path: str) -> str:
    p = pathlib.Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = p.suffix.lower()
    if ext == ".txt":
        return p.read_text(encoding="utf-8")
    elif ext == ".pdf":
        return _read_pdf(p)
    elif ext == ".docx":
        return _read_docx(p)
    else:
        raise ValueError(
            f"Unsupported file format: '{ext}'. Supported: .txt, .pdf, .docx"
        )


def _read_pdf(path: pathlib.Path) -> str:
    import fitz

    doc = fitz.open(str(path))
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()


def _read_docx(path: pathlib.Path) -> str:
    import docx

    doc = docx.Document(str(path))
    text = "\n".join(p.text for p in doc.paragraphs)
    return text.strip()
