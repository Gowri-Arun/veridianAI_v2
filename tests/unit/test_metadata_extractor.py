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

def test_parse_frontmatter_yaml_list_syntax():
    raw_md = """---
doc_id: list_doc
title: List Doc
doc_type: test_doc
quarter: Q2_2025
region: EMEA
segment: Enterprise
related_metrics: [recognized_revenue, churn_rate]
source: unit_test
---
Body content.
"""
    meta, body = parse_frontmatter(raw_md)
    assert meta["related_metrics"] == ["recognized_revenue", "churn_rate"]

def test_parse_frontmatter_leading_newline():
    raw_md = "\n\n---\ndoc_id: leading_newline\ntitle: Leading Newline\ndoc_type: test_doc\nquarter: Q3_2025\nregion: LATAM\nsegment: Mid-Market\nrelated_metrics:\n  - usage_score\nsource: unit_test\n---\nBody text.\n"
    meta, body = parse_frontmatter(raw_md)
    assert meta["doc_id"] == "leading_newline"
    assert "Body text." in body

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

def test_validate_metadata_missing_title():
    meta = {
        "doc_id": "test_doc",
        "doc_type": "policy",
        "quarter": "Q1_2025",
        "region": "APAC",
        "segment": "SMB",
        "related_metrics": ["recognized_revenue"],
        "source": "manual"
    }
    with pytest.raises(ValueError, match="'title'"):
        validate_metadata(meta)

def test_validate_metadata_missing_doc_type():
    meta = {
        "doc_id": "test_doc",
        "title": "Test",
        "quarter": "Q1_2025",
        "region": "APAC",
        "segment": "SMB",
        "related_metrics": ["recognized_revenue"],
        "source": "manual"
    }
    with pytest.raises(ValueError, match="'doc_type'"):
        validate_metadata(meta)

def test_validate_metadata_missing_quarter():
    meta = {
        "doc_id": "test_doc", "title": "Test", "doc_type": "policy",
        "region": "APAC", "segment": "SMB",
        "related_metrics": ["recognized_revenue"], "source": "manual"
    }
    with pytest.raises(ValueError, match="'quarter'"):
        validate_metadata(meta)

def test_validate_metadata_missing_region():
    meta = {
        "doc_id": "test_doc", "title": "Test", "doc_type": "policy",
        "quarter": "Q1_2025", "segment": "SMB",
        "related_metrics": ["recognized_revenue"], "source": "manual"
    }
    with pytest.raises(ValueError, match="'region'"):
        validate_metadata(meta)

def test_validate_metadata_missing_segment():
    meta = {
        "doc_id": "test_doc", "title": "Test", "doc_type": "policy",
        "quarter": "Q1_2025", "region": "APAC",
        "related_metrics": ["recognized_revenue"], "source": "manual"
    }
    with pytest.raises(ValueError, match="'segment'"):
        validate_metadata(meta)

def test_validate_metadata_missing_related_metrics():
    meta = {
        "doc_id": "test_doc", "title": "Test", "doc_type": "policy",
        "quarter": "Q1_2025", "region": "APAC", "segment": "SMB",
        "source": "manual"
    }
    with pytest.raises(ValueError, match="'related_metrics'"):
        validate_metadata(meta)

def test_validate_metadata_missing_source():
    meta = {
        "doc_id": "test_doc", "title": "Test", "doc_type": "policy",
        "quarter": "Q1_2025", "region": "APAC", "segment": "SMB",
        "related_metrics": ["recognized_revenue"]
    }
    with pytest.raises(ValueError, match="'source'"):
        validate_metadata(meta)

def test_validate_metadata_none_field():
    meta = {
        "doc_id": "test_doc", "title": None, "doc_type": "policy",
        "quarter": "Q1_2025", "region": "APAC", "segment": "SMB",
        "related_metrics": ["recognized_revenue"], "source": "manual"
    }
    with pytest.raises(ValueError, match="'title'"):
        validate_metadata(meta)

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

def test_normalize_metadata_empty_dict():
    norm = normalize_metadata({})
    assert norm == {"related_metrics": []}

def test_normalize_metadata_none_values():
    norm = normalize_metadata({
        "quarter": None,
        "region": None,
        "segment": None,
        "related_metrics": None
    })
    assert norm["related_metrics"] == []

def test_normalize_metrics_already_list():
    meta = {"related_metrics": ["revenue", "churn"]}
    norm = normalize_metadata(meta)
    assert norm["related_metrics"] == ["revenue", "churn"]

def test_normalize_metrics_non_string_list():
    meta = {"related_metrics": [123, True, None]}
    norm = normalize_metadata(meta)
    assert norm["related_metrics"] == ["123", "True", "None"]

def test_normalize_quarter_all_special_case():
    norm = normalize_metadata({"quarter": "all", "region": "global", "segment": "all"})
    assert norm["quarter"] == "All"
    assert norm["region"] == "Global"
    assert norm["segment"] == "All"

def test_extract_title():
    meta = {"title": "Metadata Title"}
    body = "# Body Heading"
    assert extract_title(meta, body) == "Metadata Title"

def test_extract_title_fallback_h1():
    meta_no_title = {}
    body_with_h1 = "\n\n# Fallback H1 Title\nSome content"
    assert extract_title(meta_no_title, body_with_h1) == "Fallback H1 Title"

def test_extract_title_empty():
    assert extract_title({}, "no heading here") == ""

def test_extract_title_prefers_metadata_over_h1():
    meta = {"title": "Explicit Title"}
    body = "# H1 Title"
    assert extract_title(meta, body) == "Explicit Title"

def test_extract_title_metadata_blank():
    meta = {"title": ""}
    body = "# H1 From Body"
    assert extract_title(meta, body) == "H1 From Body"

def test_extract_title_h1_with_trailing_spaces():
    meta = {}
    body = "#   Spaced Title   "
    assert extract_title(meta, body) == "Spaced Title"

def test_extract_title_no_h1_found():
    meta = {}
    body = "## H2 heading\n### H3 heading\nNo H1 here."
    assert extract_title(meta, body) == ""

def test_extract_title_multiple_h1_takes_first():
    meta = {}
    body = "# First H1\nSome text\n# Second H1"
    assert extract_title(meta, body) == "First H1"
