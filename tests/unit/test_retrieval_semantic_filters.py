import json
from pathlib import Path

from app.retrieval.retrieval_pipeline import RetrievalPipeline


def write_corpus(path: Path):
    chunks = [
        {"chunk_id": "c1", "doc_id": "apac", "title": "APAC", "text": "revenue enterprise decline", "metadata": {"region": "APAC", "segment": "Enterprise", "quarter": "Q4_2025", "related_metrics": ["revenue"]}},
        {"chunk_id": "c2", "doc_id": "emea", "title": "EMEA", "text": "revenue enterprise decline", "metadata": {"region": "EMEA", "segment": "Enterprise", "quarter": "Q4_2025", "related_metrics": ["revenue"]}},
        {"chunk_id": "c3", "doc_id": "smb", "title": "SMB", "text": "revenue enterprise decline", "metadata": {"region": "APAC", "segment": "SMB", "quarter": "Q4_2025", "related_metrics": ["revenue"]}},
    ]
    with open(path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + "\n")


def test_region_and_segment_filters_affect_ranking(tmp_path):
    corpus = tmp_path / "chunks.jsonl"
    write_corpus(corpus)
    pipeline = RetrievalPipeline(corpus_path=corpus)
    results = pipeline.retrieve("sales decline", top_k=3, canonical_query="revenue decline", intent_metrics=["revenue"], intent_filters={"region": "APAC", "segment": "Enterprise"})
    assert results[0].doc_id == "apac"


def test_time_filter_affects_ranking(tmp_path):
    corpus = tmp_path / "chunks.jsonl"
    write_corpus(corpus)
    pipeline = RetrievalPipeline(corpus_path=corpus)
    results = pipeline.retrieve("revenue decline", top_k=2, intent_metrics=["revenue"], intent_filters={"quarter": "Q4_2025"})
    assert all(result.score > 0 for result in results)
