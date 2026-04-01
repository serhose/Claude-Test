"""
Resume Loader — extracts text from all .docx files in source-cvs/ at startup.
"""

import pathlib
from docx import Document

SOURCES_DIR = pathlib.Path(__file__).parent.parent / "source-cvs"


def _extract_text(path: pathlib.Path) -> str:
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def load_all_resumes() -> dict[str, str]:
    """Returns {filename: full_text} for every .docx in source-cvs/."""
    resumes = {}
    for f in sorted(SOURCES_DIR.glob("*.docx")):
        try:
            resumes[f.name] = _extract_text(f)
        except Exception as e:
            print(f"Warning: could not load {f.name}: {e}")
    return resumes


# Loaded once at import time
RESUMES: dict[str, str] = load_all_resumes()
