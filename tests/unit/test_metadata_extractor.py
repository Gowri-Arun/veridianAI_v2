import pytest
from app.ingestion.metadata_extractor import (
    parse_frontmatter,
    normalize_metadata,
    validate_metadata,
    extract_title
)

def test_parse_frontmatter_valid():
    raw_md = """---
doc_id: test_doc
title: Test Title
doc_type: policy
quarter: Q1_2025
region: APAC
segment: SMB
related_metrics:
  - recognized_revenue
source: manual
---
# Main Heading
This is the body content.
"""
    meta, body = parse_frontmatter(raw_md)
    assert meta["doc_id"] == "test_doc"
    assert meta["title"] == "Test Title"
    assert "Main Heading" in body
    assert "This is the body content." in body

def test_parse_frontmatter_none():
    raw_md = "no frontmatter here"
    meta, body = parse_frontmatter(raw_md)
    assert meta == {}
    assert body == "no frontmatter here"

def test_parse_frontmatter_unclosed():
    raw_md = """---
doc_id: unclosed
title: Unclosed
# No closing marker
"""
    with pytest.raises(ValueError, match="frontmatter"):
        parse_frontmatter(raw_md)

def test_validate_metadata_valid():
    valid_meta = {
        "doc_id": "test_doc",
        "title": "Test Title",
        "doc_type": "policy",
        "quarter": "Q1_2025",
        "region": "APAC",
        "segment": "SMB",
        "related_metrics": ["recognized_revenue"],
        "source": "manual"
    }
    # Should not raise an exception
    validate_metadata(valid_meta)

def test_validate_metadata_missing_doc_id():
    invalid_meta = {
        "title": "Test Title",
        "doc_type": "policy",
        "quarter": "Q1_2025",
        "region": "APAC",
        "segment": "SMB",
        "related_metrics": ["recognized_revenue"],
        "source": "manual"
    }
    with pytest.raises(ValueError, match="Missing required metadata field: 'doc_id'"):
        validate_metadata(invalid_meta)

def test_validate_metadata_invalid_quarter():
    invalid_meta = {
        "doc_id": "test_doc",
        "title": "Test Title",
        "doc_type": "policy",
        "quarter": "Q5_2025",  # Invalid
        "region": "APAC",
        "segment": "SMB",
        "related_metrics": ["recognized_revenue"],
        "source": "manual"
    }
    with pytest.raises(ValueError, match="Invalid quarter"):
        validate_metadata(invalid_meta)

def test_validate_metadata_invalid_region():
    invalid_meta = {
        "doc_id": "test_doc",
        "title": "Test Title",
        "doc_type": "policy",
        "quarter": "Q1_2025",
        "region": "Mars",  # Invalid
        "segment": "SMB",
        "related_metrics": ["recognized_revenue"],
        "source": "manual"
    }
    with pytest.raises(ValueError, match="Invalid region"):
        validate_metadata(invalid_meta)

def test_validate_metadata_invalid_segment():
    invalid_meta = {
        "doc_id": "test_doc",
        "title": "Test Title",
        "doc_type": "policy",
        "quarter": "Q1_2025",
        "region": "APAC",
        "segment": "Mega-Enterprise",  # Invalid
        "related_metrics": ["recognized_revenue"],
        "source": "manual"
    }
    with pytest.raises(ValueError, match="Invalid segment"):
        validate_metadata(invalid_meta)

def test_normalize_metadata_metrics_handling():
    # Test related_metrics as list of non-strings or comma-separated string
    meta_with_string = {
        "quarter": "q1_2025",
        "region": "apac",
        "segment": "smb",
        "related_metrics": "recognized_revenue, bookings"
    }
    norm = normalize_metadata(meta_with_string)
    assert norm["quarter"] == "Q1_2025"  # Capitalization normalization
    assert norm["region"] == "APAC"
    assert norm["segment"] == "SMB"
    assert norm["related_metrics"] == ["recognized_revenue", "bookings"]

def test_extract_title():
    # 1. From metadata title
    meta = {"title": "Metadata Title"}
    body = "# Body Heading"
    assert extract_title(meta, body) == "Metadata Title"
    
    # 2. From body H1 fallback
    meta_no_title = {}
    body_with_h1 = "\n\n# Fallback H1 Title\nSome content"
    assert extract_title(meta_no_title, body_with_h1) == "Fallback H1 Title"
    
    # 3. Completely empty
    assert extract_title({}, "no heading here") == ""
