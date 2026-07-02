"""Data source abstraction — format dispatcher.

Routes parsing by file type or directory structure. All paths return
a CourseModule for uniform downstream processing.
"""

from __future__ import annotations

import os
import tempfile
import zipfile
from pathlib import Path

from dialog.agents.utils.agent_states import (
    AgentState,
    ContentPage,
    CourseModule,
)


SUPPORTED_EXTENSIONS = {".zip", ".pdf", ".docx", ".txt", ".md"}


def parse_document(state: AgentState) -> dict:
    """Dispatch to the correct parser and return a CourseModule.

    This is a graph node. It detects the input format and routes to
    the appropriate parser. All parsers return the same CourseModule
    structure.

    Also sets raw_text as the concatenation of all page texts for
    backward compatibility with the semantic_chunker.
    """
    source = state.get("source_path", "")
    if not source:
        return {"error": "No source_path provided"}

    try:
        course_module = dispatch(source)
    except (ValueError, OSError) as e:
        return {"error": str(e)}

    # Build raw_text from all pages for backward compatibility
    raw_text = "\n\n".join(
        f"## {page['title']}\n\n{page['text']}" for page in course_module["pages"]
    )

    return {"course_module": course_module, "raw_text": raw_text}


def dispatch(source: str) -> CourseModule:
    """Detect format and route to the correct parser.

    Args:
        source: Path to a file or directory.

    Returns:
        CourseModule structure.

    Raises:
        ValueError: If the format is unsupported.
    """
    path = Path(source)

    # Directory input
    if path.is_dir():
        return _dispatch_directory(path)

    # File input
    if not path.is_file():
        raise ValueError(f"Source path does not exist: {source}")

    ext = path.suffix.lower()

    if ext == ".zip":
        return _dispatch_zip(path)
    elif ext == ".pdf":
        return _dispatch_pdf(path)
    elif ext == ".docx":
        return _dispatch_docx(path)
    elif ext in (".txt", ".md"):
        return _dispatch_text(path)
    else:
        raise ValueError(
            f"Unsupported file format: '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )


def _dispatch_directory(path: Path) -> CourseModule:
    """Handle directory input — check for D2L structure."""
    toc = path / "Table of Contents.html"
    if toc.exists():
        from .d2l_parser import parse_d2l_folder
        return parse_d2l_folder(str(path))
    else:
        raise ValueError(
            f"Unsupported directory layout: no 'Table of Contents.html' found in {path}"
        )


def _dispatch_zip(path: Path) -> CourseModule:
    """Unzip to temp directory and re-dispatch as directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        with zipfile.ZipFile(str(path), "r") as zf:
            zf.extractall(tmp_dir)

        # The zip might contain a single top-level folder or files directly
        contents = os.listdir(tmp_dir)
        if len(contents) == 1 and (Path(tmp_dir) / contents[0]).is_dir():
            extract_root = str(Path(tmp_dir) / contents[0])
        else:
            extract_root = tmp_dir

        return dispatch(extract_root)


def _dispatch_pdf(path: Path) -> CourseModule:
    """Wrap a single PDF in a CourseModule."""
    from .pdf_parser import extract_pdf

    text = extract_pdf(str(path))
    return _wrap_single_file(path, text, "pdf")


def _dispatch_docx(path: Path) -> CourseModule:
    """Wrap a single Word doc in a CourseModule."""
    from .docx_parser import extract_docx

    text = extract_docx(str(path))
    return _wrap_single_file(path, text, "docx")


def _dispatch_text(path: Path) -> CourseModule:
    """Wrap a single text/markdown file in a CourseModule."""
    from .text_parser import extract_text

    text = extract_text(str(path))
    return _wrap_single_file(path, text, "text")


def _wrap_single_file(path: Path, text: str, content_type: str) -> CourseModule:
    """Wrap extracted text from a single file into a CourseModule."""
    page = ContentPage(
        page_number=1,
        title=path.stem,
        source_file=path.name,
        content_type=content_type,
        text=text,
    )
    return CourseModule(
        course_name=path.stem,
        module_id="single",
        source_folder=str(path.parent),
        pages=[page],
    )
