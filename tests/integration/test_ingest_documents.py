import json
from pathlib import Path
from scripts.ingest_documents import main

FORBIDDEN_KEYWORD = "Analyst" + "Graph"

def test_ingest_documents_integration():
    chunks_path = Path("data/processed/document_chunks.jsonl")
    metadata_path = Path("data/processed/document_metadata.jsonl")
    snapshot_path = Path("data/processed/schema_snapshot.json")
    
    # 1. Run ingestion script
    main()
    
    # 2. Check generated files exist
    assert chunks_path.exists(), "document_chunks.jsonl should be generated"
    assert metadata_path.exists(), "document_metadata.jsonl should be generated"
    assert snapshot_path.exists(), "schema_snapshot.json should be generated"
    
    # 3. Validate JSONL files contain no empty lines after strip()
    chunk_raw = chunks_path.read_text(encoding="utf-8")
    meta_raw = metadata_path.read_text(encoding="utf-8")
    
    for idx, line in enumerate(chunk_raw.splitlines(), 1):
        assert line.strip(), f"document_chunks.jsonl contains empty line at line {idx}"
        
    for idx, line in enumerate(meta_raw.splitlines(), 1):
        assert line.strip(), f"document_metadata.jsonl contains empty line at line {idx}"

    # 4. Validate metadata records count
    meta_lines = meta_raw.splitlines()
    assert len(meta_lines) == 20, f"Expected exactly 20 metadata records, got {len(meta_lines)}"
    
    for line in meta_lines:
        rec = json.loads(line)
        required_fields = ["doc_id", "title", "doc_type", "quarter", "region", "segment", "related_metrics", "source", "source_path"]
        for f in required_fields:
            assert f in rec, f"Missing required field '{f}' in metadata record: {rec}"
        assert FORBIDDEN_KEYWORD not in line, "Forbidden legacy keyword found in metadata record line!"
        
    # 5. Validate document_chunks.jsonl
    chunk_lines = chunk_raw.splitlines()
    assert len(chunk_lines) >= 20, f"Expected at least 20 chunks, got {len(chunk_lines)}"
    
    chunk_ids = set()
    for line in chunk_lines:
        chunk = json.loads(line)
        required_fields = ["chunk_id", "doc_id", "title", "doc_type", "text", "chunk_index", "metadata", "source_path"]
        for f in required_fields:
            assert f in chunk, f"Missing required field '{f}' in chunk: {chunk}"
            
        # Check every chunk_id is unique
        assert chunk["chunk_id"] not in chunk_ids, f"Duplicate chunk_id found: {chunk['chunk_id']}"
        chunk_ids.add(chunk["chunk_id"])
        
        # Check chunk text is non-empty
        assert chunk["text"].strip(), f"Empty chunk text found in chunk_id: {chunk['chunk_id']}"
        
        # Check every chunk preserves source_path
        source_path = chunk["source_path"]
        assert source_path, f"Empty source_path in chunk: {chunk['chunk_id']}"
        assert source_path.endswith(".md"), f"source_path should end with .md, got: {source_path}"
        assert "data/raw/unstructured" in source_path.replace("\\", "/"), f"source_path should refer to a file under data/raw/unstructured/, got: {source_path}"
        
        # Check every chunk has metadata.related_metrics as a non-empty list
        assert "metadata" in chunk
        assert "related_metrics" in chunk["metadata"], f"Missing related_metrics in metadata for chunk {chunk['chunk_id']}"
        assert isinstance(chunk["metadata"]["related_metrics"], list), f"related_metrics must be a list in chunk {chunk['chunk_id']}"
        assert len(chunk["metadata"]["related_metrics"]) > 0, f"related_metrics must be a non-empty list in chunk {chunk['chunk_id']}"
        
        assert FORBIDDEN_KEYWORD not in line, "Forbidden legacy keyword found in chunk line!"
        
    # 6. Validate schema_snapshot.json
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    
    assert snapshot["number_of_documents"] == 20, f"Expected exactly 20 documents, got {snapshot['number_of_documents']}"
    assert snapshot["number_of_chunks"] >= 20, f"Expected at least 20 chunks, got {snapshot['number_of_chunks']}"
    assert isinstance(snapshot["document_types"], dict)
    assert isinstance(snapshot["quarters"], dict)
    assert isinstance(snapshot["regions"], dict)
    assert isinstance(snapshot["segments"], dict)
    assert isinstance(snapshot["related_metrics"], list)
    assert isinstance(snapshot["source_files"], list)
    assert "generated_at" in snapshot
    
    # Assert schema_snapshot.json contains all expected regions and segments keys
    expected_regions = {"APAC", "EMEA", "North America", "LATAM", "Global"}
    expected_segments = {"SMB", "Mid-Market", "Enterprise", "All"}
    
    snapshot_regions = set(snapshot["regions"].keys())
    snapshot_segments = set(snapshot["segments"].keys())
    
    for r in expected_regions:
        assert r in snapshot_regions, f"Expected region '{r}' missing from snapshot regions: {snapshot_regions}"
        
    for s in expected_segments:
        assert s in snapshot_segments, f"Expected segment '{s}' missing from snapshot segments: {snapshot_segments}"
        
    assert FORBIDDEN_KEYWORD not in snapshot_path.read_text(encoding="utf-8"), "Forbidden legacy keyword found in schema snapshot!"
