import json
import pytest
from pathlib import Path

from app.retrieval.bm25_retriever import BM25Retriever


@pytest.fixture
def small_corpus(tmp_path: Path) -> Path:
    corpus_path = tmp_path / "test_chunks.jsonl"
    chunks = [
        {
            "chunk_id": "c1",
            "doc_id": "d1",
            "title": "Revenue Report",
            "text": "revenue in APAC grew by 15 percent in Q1 2025",
            "metadata": {"region": "APAC"},
            "source_path": "reports/q1_2025.md",
        },
        {
            "chunk_id": "c2",
            "doc_id": "d2",
            "title": "Churn Analysis",
            "text": "customer churn rate increased in EMEA region last quarter",
            "metadata": {"region": "EMEA"},
            "source_path": "reports/churn_q4_2024.md",
        },
        {
            "chunk_id": "c3",
            "doc_id": "d3",
            "title": "Marketing Spend",
            "text": "marketing spend in north america was 2 million dollars",
            "metadata": {"region": "North America"},
            "source_path": "reports/marketing_2025.md",
        },
        {
            "chunk_id": "c4",
            "doc_id": "d4",
            "title": "Support Tickets",
            "text": "support ticket volume increased in enterprise segment",
            "metadata": {"segment": "Enterprise"},
            "source_path": "reports/support_q1.md",
        },
        {
            "chunk_id": "c5",
            "doc_id": "d5",
            "title": "Sales Pipeline",
            "text": "sales pipeline value grew faster than revenue in Q2 2025",
            "metadata": {"quarter": "Q2_2025"},
            "source_path": "reports/pipeline.md",
        },
    ]
    with open(corpus_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + "\n")
    return corpus_path


class TestBM25Retriever:
    def test_retrieve_revenue(self, small_corpus: Path):
        retriever = BM25Retriever(corpus_path=small_corpus)
        results = retriever.retrieve("revenue growth", top_k=3)
        assert len(results) <= 3
        scores = [r.score for r in results]
        assert all(s >= 0 for s in scores)

    def test_retrieve_churn(self, small_corpus: Path):
        retriever = BM25Retriever(corpus_path=small_corpus)
        results = retriever.retrieve("customer churn", top_k=3)
        assert len(results) >= 1

    def test_top_k_returned(self, small_corpus: Path):
        retriever = BM25Retriever(corpus_path=small_corpus)
        results = retriever.retrieve("revenue churn marketing pipeline", top_k=5)
        assert len(results) <= 5
        assert len(results) >= 1

    def test_empty_corpus(self, tmp_path: Path):
        empty_path = tmp_path / "empty.jsonl"
        empty_path.write_text("", encoding="utf-8")
        retriever = BM25Retriever(corpus_path=empty_path)
        results = retriever.retrieve("anything", top_k=5)
        assert results == []

    def test_non_existent_corpus(self, tmp_path: Path):
        missing_path = tmp_path / "missing.jsonl"
        retriever = BM25Retriever(corpus_path=missing_path)
        results = retriever.retrieve("anything", top_k=5)
        assert results == []

    def test_score_uniqueness(self, small_corpus: Path):
        retriever = BM25Retriever(corpus_path=small_corpus)
        results = retriever.retrieve("revenue in APAC grew by 15 percent", top_k=3)
        assert len(results) >= 1
        assert results[0].score > 0

    def test_empty_query(self, small_corpus: Path):
        retriever = BM25Retriever(corpus_path=small_corpus)
        results = retriever.retrieve("")
        assert len(results) == 0

    def test_retrieved_chunk_fields(self, small_corpus: Path):
        retriever = BM25Retriever(corpus_path=small_corpus)
        results = retriever.retrieve("revenue APAC", top_k=1)
        if results:
            r = results[0]
            assert r.chunk_id is not None
            assert r.title is not None
            assert r.metadata is not None
