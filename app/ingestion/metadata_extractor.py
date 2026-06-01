import yaml
import re
from typing import Any

ALLOWED_QUARTERS = {"Q1_2025", "Q2_2025", "Q3_2025", "Q4_2025", "All"}
ALLOWED_REGIONS = {"APAC", "EMEA", "North America", "LATAM", "Global"}
ALLOWED_SEGMENTS = {"SMB", "Mid-Market", "Enterprise", "All"}
REQUIRED_FIELDS = {"doc_id", "title", "doc_type", "quarter", "region", "segment", "related_metrics", "source"}

def parse_frontmatter(markdown_text: str) -> tuple[dict[str, Any], str]:
    """
    Parses YAML-style frontmatter from markdown text.
    Returns a tuple containing the parsed metadata dictionary and the remaining body text.
    """
    if not markdown_text.strip().startswith("---"):
        return {}, markdown_text

    # Match everything between the first two '---' markers
    match = re.match(r"^---\s*\n(.*?)\n---[\s]*\n(.*)$", markdown_text.lstrip(), re.DOTALL)
    if not match:
        raise ValueError("Malformed or unclosed YAML frontmatter boundary.")

    frontmatter_str, body_text = match.groups()
    try:
        metadata = yaml.safe_load(frontmatter_str) or {}
        if not isinstance(metadata, dict):
            metadata = {}
    except Exception:
        metadata = {}
        body_text = markdown_text

    return metadata, body_text

def normalize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Normalizes metadata values (e.g., quarter, region, segment, related_metrics).
    """
    normalized = metadata.copy()

    # Normalize quarter
    if "quarter" in normalized and isinstance(normalized["quarter"], str):
        val = normalized["quarter"].strip()
        # Handle capitalization differences
        for allowed in ALLOWED_QUARTERS:
            if val.lower() == allowed.lower():
                normalized["quarter"] = allowed
                break

    # Normalize region
    if "region" in normalized and isinstance(normalized["region"], str):
        val = normalized["region"].strip()
        for allowed in ALLOWED_REGIONS:
            if val.lower() == allowed.lower():
                normalized["region"] = allowed
                break

    # Normalize segment
    if "segment" in normalized and isinstance(normalized["segment"], str):
        val = normalized["segment"].strip()
        for allowed in ALLOWED_SEGMENTS:
            if val.lower() == allowed.lower():
                normalized["segment"] = allowed
                break

    # Normalize related_metrics to be a list of strings
    if "related_metrics" in normalized:
        metrics = normalized["related_metrics"]
        if isinstance(metrics, str):
            normalized["related_metrics"] = [m.strip() for m in metrics.split(",") if m.strip()]
        elif isinstance(metrics, list):
            normalized["related_metrics"] = [str(m).strip() for m in metrics]
        else:
            normalized["related_metrics"] = []
    else:
        normalized["related_metrics"] = []

    return normalized

def validate_metadata(metadata: dict[str, Any]) -> None:
    """
    Validates that the required metadata fields are present and have valid values.
    Raises ValueError for invalid or missing required metadata.
    """
    # Check for missing required fields
    for field in REQUIRED_FIELDS:
        if field not in metadata or metadata[field] is None:
            raise ValueError(f"Missing required metadata field: '{field}'")

    # Validate quarter
    q = metadata["quarter"]
    if q not in ALLOWED_QUARTERS:
        raise ValueError(f"Invalid quarter: '{q}'. Allowed values: {ALLOWED_QUARTERS}")

    # Validate region
    r = metadata["region"]
    if r not in ALLOWED_REGIONS:
        raise ValueError(f"Invalid region: '{r}'. Allowed values: {ALLOWED_REGIONS}")

    # Validate segment
    s = metadata["segment"]
    if s not in ALLOWED_SEGMENTS:
        raise ValueError(f"Invalid segment: '{s}'. Allowed values: {ALLOWED_SEGMENTS}")

    # Validate related_metrics is a list
    if not isinstance(metadata["related_metrics"], list):
        raise ValueError("Field 'related_metrics' must be a list of strings.")

def extract_title(metadata: dict[str, Any], body: str) -> str:
    """
    Extracts the document title. Uses metadata title if present,
    otherwise falls back to the first H1 tag in the body text.
    """
    if "title" in metadata and isinstance(metadata["title"], str) and metadata["title"].strip():
        return metadata["title"].strip()

    # Search for the first line starting with '# ' in the body
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
            if title:
                return title

    return ""
