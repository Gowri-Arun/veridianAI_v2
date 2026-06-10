from fastapi import APIRouter

from app.schemas.query import QueryRequest, QueryResponse
from app.schemas.trace import TraceStep
from app.agents.intent_agent import IntentAgent
from app.semantic_layer.semantic_parser import SemanticParser
from app.retrieval.retrieval_pipeline import RetrievalPipeline

router = APIRouter(prefix="/api", tags=["query"])
intent_agent = IntentAgent()
semantic_parser = SemanticParser()
retrieval_pipeline = RetrievalPipeline()


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    trace: list[TraceStep] = []

    intent_result = intent_agent.classify(req.query)
    if req.include_trace:
        trace.append(
            TraceStep(
                step_name="intent_classification",
                status="completed",
                input_summary=req.query[:120],
                output_summary=f"type={intent_result.query_type}, confidence={intent_result.confidence:.2f}",
                metadata=intent_result.model_dump(),
            )
        )

    semantic_result = semantic_parser.parse(req.query)
    if req.include_trace:
        trace.append(
            TraceStep(
                step_name="semantic_parsing",
                status="completed",
                input_summary=req.query[:120],
                output_summary=f"metrics={semantic_result['metrics']}, filters={semantic_result['filters']}",
                metadata=semantic_result,
            )
        )

    retrieved_docs: list[dict] = []
    if intent_result.requires_retrieval:
        results = retrieval_pipeline.retrieve(
            req.query,
            top_k=req.top_k,
            intent_metrics=intent_result.metrics,
            intent_filters=intent_result.filters,
        )
        retrieved_docs = [r.model_dump() for r in results]
        if req.include_trace:
            trace.append(
                TraceStep(
                    step_name="retrieval",
                    status="completed",
                    input_summary=req.query[:120],
                    output_summary=f"retrieved {len(retrieved_docs)} chunks via BM25",
                    metadata={"top_k": req.top_k, "result_count": len(retrieved_docs)},
                )
            )
    else:
        if req.include_trace:
            trace.append(
                TraceStep(
                    step_name="retrieval",
                    status="skipped",
                    input_summary="retrieval not required by intent classifier",
                    output_summary=None,
                    metadata={"reason": intent_result.rationale},
                )
            )

    trace_dicts = [t.model_dump() for t in trace]

    status = "completed"
    message = None
    if intent_result.query_type in ("adversarial", "unanswerable"):
        status = "rejected"
        message = intent_result.rationale
    elif intent_result.query_type in ("ambiguous",):
        status = "needs_clarification"
        message = intent_result.rationale

    return QueryResponse(
        query=req.query,
        status=status,
        intent=intent_result.model_dump(),
        semantic_mapping=semantic_result,
        retrieved_documents=retrieved_docs,
        trace=trace_dicts if req.include_trace else [],
        message=message,
    )
