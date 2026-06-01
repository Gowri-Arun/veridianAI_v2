from pathlib import Path
from typing import Any
from pydantic import BaseModel
from app.ingestion.metadata_extractor import (
    parse_frontmatter,
    normalize_metadata,
    validate_metadata,
    extract_title
)

class Document(BaseModel):
    doc_id: str
    title: str
    doc_type: str
    text: str
    metadata: dict[str, Any]
    source_path: str

def load_document(path: str | Path) -> Document:
    """
    Loads a single markdown document from the filesystem, extracts its
    frontmatter and body, validates its metadata, and returns a Document object.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    with open(path_obj, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # Parse YAML frontmatter and body
    raw_metadata, body_text = parse_frontmatter(raw_content)

    # Normalize metadata
    metadata = normalize_metadata(raw_metadata)

    # If title is missing in metadata, extract it from body
    if "title" not in metadata or not metadata["title"]:
        metadata["title"] = extract_title(metadata, body_text)

    # If doc_id is missing, default to the file's stem name
    if "doc_id" not in metadata or not metadata["doc_id"]:
        metadata["doc_id"] = path_obj.stem

    # If doc_type is missing, default to a fallback
    if "doc_type" not in metadata or not metadata["doc_type"]:
        metadata["doc_type"] = "document"

    # Validate required metadata
    validate_metadata(metadata)

    # Validate that body is not empty
    if not body_text.strip():
        raise ValueError("Document body text is empty.")

    # Build Pydantic Document
    return Document(
        doc_id=metadata["doc_id"],
        title=metadata["title"],
        doc_type=metadata["doc_type"],
        text=body_text,
        metadata=metadata,
        source_path=str(path_obj.resolve())
    )

def load_documents(directory: str | Path) -> list[Document]:
    """
    Loads and validates all markdown documents (.md) within the specified directory.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    documents = []
    # Search for all .md files in the directory
    for file_path in sorted(dir_path.glob("*.md")):
        try:
            doc = load_document(file_path)
            documents.append(doc)
        except ValueError as e:
            # Re-raise or handle as requested (we must not silently ignore invalid metadata)
            raise ValueError(f"Metadata validation failed for file {file_path}: {e}") from e

    return documents
