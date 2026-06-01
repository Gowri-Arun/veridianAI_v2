import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
from app.ingestion.document_loader import load_documents
from app.ingestion.chunker import chunk_documents

EXPECTED_REGIONS = ("APAC", "EMEA", "North America", "LATAM", "Global")
EXPECTED_SEGMENTS = ("SMB", "Mid-Market", "Enterprise", "All")

def write_jsonl(records: list[dict[str, Any]], path: str | Path) -> None:
    """Writes a list of dictionaries to a JSONL file."""
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(path_obj, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def write_json(data: dict[str, Any], path: str | Path) -> None:
    """Writes a dictionary to a JSON file."""
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(path_obj, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def build_document_corpus(input_dir: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """
    Loads markdown documents, chunks them, writes processed JSONL and JSON files,
    and returns a summary dictionary of the schema snapshot.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Load documents
    documents = load_documents(input_path)
    
    # 2. Chunk documents
    chunks = chunk_documents(documents)
    
    # 3. Create document_chunks.jsonl records
    chunk_records = [chunk.model_dump() for chunk in chunks]
    write_jsonl(chunk_records, output_path / "document_chunks.jsonl")
    
    # 4. Create document_metadata.jsonl records
    metadata_records = []
    doc_types = {}
    quarters = {}
    regions = {}
    segments = {}
    unique_related_metrics = set()
    source_files = []
    
    for doc in documents:
        meta = doc.metadata
        
        # Build metadata record
        meta_rec = {
            "doc_id": doc.doc_id,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "quarter": meta.get("quarter", "All"),
            "region": meta.get("region", "Global"),
            "segment": meta.get("segment", "All"),
            "related_metrics": meta.get("related_metrics", []),
            "source": meta.get("source", "unknown"),
            "source_path": doc.source_path
        }
        metadata_records.append(meta_rec)
        
        # Collect statistics for snapshot
        doc_types[doc.doc_type] = doc_types.get(doc.doc_type, 0) + 1
        q_val = meta.get("quarter", "All")
        quarters[q_val] = quarters.get(q_val, 0) + 1
        r_val = meta.get("region", "Global")
        regions[r_val] = regions.get(r_val, 0) + 1
        s_val = meta.get("segment", "All")
        segments[s_val] = segments.get(s_val, 0) + 1
        
        for m in meta.get("related_metrics", []):
            unique_related_metrics.add(m)
            
        source_files.append(Path(doc.source_path).name)

    for region in EXPECTED_REGIONS:
        regions.setdefault(region, 0)
    for segment in EXPECTED_SEGMENTS:
        segments.setdefault(segment, 0)
        
    write_jsonl(metadata_records, output_path / "document_metadata.jsonl")
    
    # 5. Create schema_snapshot.json
    snapshot = {
        "number_of_documents": len(documents),
        "number_of_chunks": len(chunks),
        "document_types": doc_types,
        "quarters": quarters,
        "regions": regions,
        "segments": segments,
        "related_metrics": sorted(list(unique_related_metrics)),
        "source_files": sorted(source_files),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    write_json(snapshot, output_path / "schema_snapshot.json")
    
    return snapshot
