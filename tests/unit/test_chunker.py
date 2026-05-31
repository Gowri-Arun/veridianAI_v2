from app.ingestion.chunker import split_into_sections, chunk_text, chunk_document, chunk_documents, DocumentChunk
from app.ingestion.document_loader import Document

FORBIDDEN_KEYWORD = "Analyst" + "Graph"

def test_split_into_sections_detects_headings():
    raw_md = """# Intro Heading
Some intro text.
## Section A
Text under section A.
### Sub Section B
Text under sub B.
"""
    sections = split_into_sections(raw_md)
    assert len(sections) == 3
    assert sections[0]["heading"] == "Intro Heading"
    assert "Some intro text." in sections[0]["text"]
    assert sections[1]["heading"] == "Section A"
    assert "Text under section A." in sections[1]["text"]
    assert sections[2]["heading"] == "Sub Section B"

def test_chunk_text_non_empty():
    text = "this is some sample text for testing the chunker functions."
    chunks = chunk_text(text, target_words=5, overlap_words=1)
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.strip(), "Chunk must be non-empty"

def test_chunk_text_applies_overlap():
    text = "one two three four five six seven eight nine ten"
    # Target 5 words, overlap 2 words
    # First chunk: one two three four five
    # Second chunk: four five six seven eight (overlap starts from index 3 'four')
    # Third chunk: seven eight nine ten (overlap starts from index 6 'seven')
    chunks = chunk_text(text, target_words=5, overlap_words=2)
    assert len(chunks) == 3
    assert chunks[0] == "one two three four five"
    assert chunks[1] == "four five six seven eight"
    assert chunks[2] == "seven eight nine ten"

def test_chunk_document_preserves_attributes():
    doc = Document(
        doc_id="test_doc",
        title="Test Document",
        doc_type="policy",
        text="""# Section 1
This is the content under section 1. It is short.
# Section 2
This is the content under section 2.""",
        metadata={
            "quarter": "Q1_2025",
            "region": "APAC",
            "segment": "SMB",
            "related_metrics": ["churn_rate"],
            "source": "unit_test"
        },
        source_path="/path/to/test_doc.md"
    )
    
    chunks = chunk_document(doc, target_words=10, overlap_words=2)
    assert len(chunks) == 2
    
    # Assert properties preserved
    assert chunks[0].doc_id == "test_doc"
    assert chunks[0].title == "Test Document"
    assert chunks[0].doc_type == "policy"
    assert chunks[0].metadata["region"] == "APAC"
    assert chunks[0].source_path == "/path/to/test_doc.md"
    
    # Assert unique deterministic chunk_ids
    assert chunks[0].chunk_id == "test_doc::chunk_000"
    assert chunks[1].chunk_id == "test_doc::chunk_001"
    
    # Check no restricted legacy project name in chunks
    for chunk in chunks:
        assert FORBIDDEN_KEYWORD not in chunk.text
        assert FORBIDDEN_KEYWORD not in chunk.chunk_id

def test_chunk_documents_works_for_multiple():
    doc1 = Document(
        doc_id="doc1",
        title="Doc 1",
        doc_type="policy",
        text="Some text under doc 1.",
        metadata={"quarter": "All", "region": "Global", "segment": "All", "related_metrics": [], "source": "test"},
        source_path="/path/1"
    )
    doc2 = Document(
        doc_id="doc2",
        title="Doc 2",
        doc_type="policy",
        text="Some text under doc 2.",
        metadata={"quarter": "All", "region": "Global", "segment": "All", "related_metrics": [], "source": "test"},
        source_path="/path/2"
    )
    
    chunks = chunk_documents([doc1, doc2])
    assert len(chunks) == 2
    assert chunks[0].doc_id == "doc1"
    assert chunks[1].doc_id == "doc2"
