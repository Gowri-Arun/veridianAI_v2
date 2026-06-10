import pytest
from pydantic import ValidationError

from app.schemas.query import QueryRequest, QueryResponse
from app.schemas.intent import IntentClassification
from app.schemas.retrieval import RetrievedChunk
from app.schemas.trace import TraceStep


class TestQueryRequest:
    def test_valid_query(self):
        req = QueryRequest(query="what is revenue in APAC")
        assert req.query == "what is revenue in APAC"
        assert req.top_k == 5
        assert req.include_trace is True

    def test_custom_top_k(self):
        req = QueryRequest(query="revenue churn", top_k=10)
        assert req.top_k == 10

    def test_invalid_short_query(self):
        with pytest.raises(ValidationError):
            QueryRequest(query="ab")

    def test_invalid_top_k_high(self):
        with pytest.raises(ValidationError):
            QueryRequest(query="revenue", top_k=50)


class TestQueryResponse:
    def test_basic_response(self):
        resp = QueryResponse(
            query="revenue in APAC",
            status="completed",
        )
        assert resp.query == "revenue in APAC"
        assert resp.status == "completed"
        assert resp.intent is None
        assert resp.retrieved_documents == []

    def test_full_response(self):
        resp = QueryResponse(
            query="test",
            status="completed",
            intent={"query_type": "simple_sql", "confidence": 0.8, "rationale": "test"},
            semantic_mapping={"metrics": ["revenue"]},
            retrieved_documents=[{"chunk_id": "1", "score": 0.95}],
            trace=[{"step_name": "intent", "status": "ok"}],
        )
        assert resp.intent["query_type"] == "simple_sql"
        assert len(resp.retrieved_documents) == 1


class TestIntentSchema:
    def test_valid_intent(self):
        ic = IntentClassification(
            query_type="simple_document",
            confidence=0.85,
            rationale="test",
        )
        assert ic.query_type == "simple_document"
        assert ic.requires_retrieval is False

    def test_invalid_type(self):
        with pytest.raises(ValidationError):
            IntentClassification(
                query_type="invalid_type",
                confidence=0.5,
                rationale="test",
            )

    def test_invalid_confidence_high(self):
        with pytest.raises(ValidationError):
            IntentClassification(
                query_type="simple_document",
                confidence=1.5,
                rationale="test",
            )


class TestRetrievalSchema:
    def test_chunk_fields(self):
        chunk = RetrievedChunk(
            chunk_id="c1",
            doc_id="d1",
            title="Test Doc",
            text="Some text",
            score=0.95,
            rank=1,
            metadata={"source": "test"},
        )
        assert chunk.chunk_id == "c1"
        assert chunk.rank == 1


class TestTraceSchema:
    def test_trace_step(self):
        step = TraceStep(
            step_name="intent",
            status="completed",
        )
        assert step.step_name == "intent"
        assert step.input_summary is None
