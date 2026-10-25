from collections.abc import Callable
from datetime import datetime, timezone
import time
from typing import Any

from fastapi import APIRouter

from app.agents.intent_agent import IntentAgent
from app.retrieval.retrieval_pipeline import RetrievalPipeline
from app.schemas.query import QueryRequest, QueryResponse
from app.schemas.trace import ExecutionTraceStep
from app.semantic_layer.semantic_parser import SemanticParser
from app.sql_engine.comparison import calculate_comparison
from app.sql_engine.compiler import SQLCompiler
from app.sql_engine.executor import DuckDBExecutor
from app.sql_engine.planner import StructuredQueryPlanner
from app.sql_engine.safety import SQLSafetyValidator

router = APIRouter(prefix="/api", tags=["query"])
intent_agent = IntentAgent()
semantic_parser = SemanticParser()
retrieval_pipeline = RetrievalPipeline()
planner = StructuredQueryPlanner()
compiler = SQLCompiler()
safety_validator = SQLSafetyValidator()
executor = DuckDBExecutor()


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    trace: list[ExecutionTraceStep] = []

    intent_result = _run_stage(
        trace,
        "intent_classification",
        lambda: intent_agent.classify(req.query),
        input_summary=req.query[:120],
    )

    semantic_result = _run_stage(
        trace,
        "semantic_parsing",
        lambda: semantic_parser.parse_typed(req.query),
        input_summary=req.query[:120],
    )

    sql_plan = None
    compiled_queries = []
    sql_results = []
    comparison_results = []
    errors: list[dict[str, Any] | str] = [e.model_dump() for e in semantic_result.errors]
    warnings: list[dict[str, Any] | str] = [w.model_dump() for w in semantic_result.warnings]

    blocked = intent_result.query_type in ("adversarial", "unanswerable") or semantic_result.requires_clarification or bool(semantic_result.errors)
    if intent_result.requires_sql and not blocked:
        sql_plan = _run_stage(
            trace,
            "sql_planning",
            lambda: planner.plan(semantic_result),
            input_summary=f"metrics={[m.canonical_name for m in semantic_result.metrics]}",
        )
        errors.extend([e.model_dump() for e in sql_plan.errors])
        warnings.extend(sql_plan.warnings)

        if sql_plan.specs and not sql_plan.errors:
            for spec in sql_plan.specs:
                compiled = _run_stage(
                    trace,
                    "sql_compilation",
                    lambda spec=spec: compiler.compile(spec),
                    input_summary=f"{spec.query_shape}:{spec.metric}",
                )
                safety_error = _run_stage(
                    trace,
                    "sql_safety_validation",
                    lambda compiled=compiled: safety_validator.validate(compiled),
                    input_summary=compiled.query_id,
                )
                if safety_error:
                    errors.append(safety_error.model_dump())
                    continue
                compiled_queries.append(compiled)
                result = _run_stage(
                    trace,
                    "sql_execution",
                    lambda compiled=compiled: executor.execute(compiled),
                    input_summary=compiled.query_id,
                )
                sql_results.append(result)
                if result.error:
                    errors.append(result.error.model_dump())
                comparison = calculate_comparison(spec, result)
                if comparison:
                    comparison_results.append(comparison)
                    trace.append(_trace_step("comparison_calculation", "completed", input_summary=spec.query_id, output_summary=comparison.direction))
    elif intent_result.requires_sql:
        reason = "semantic clarification or error" if not intent_result.query_type in ("adversarial", "unanswerable") else intent_result.rationale
        trace.append(_trace_step("sql_planning", "skipped", input_summary="SQL required but blocked", output_summary=reason))
    else:
        trace.append(_trace_step("sql_planning", "skipped", input_summary="SQL not required by intent classifier"))

    retrieved_docs: list[dict[str, Any]] = []
    if intent_result.requires_retrieval and intent_result.query_type not in ("adversarial", "unanswerable"):
        try:
            filter_dict = {f.dimension: f.value for f in semantic_result.filters}
            metric_names = [m.canonical_name for m in semantic_result.metrics]
            results = _run_stage(
                trace,
                "retrieval",
                lambda: retrieval_pipeline.retrieve(
                    req.query,
                    top_k=req.top_k,
                    intent_metrics=metric_names,
                    intent_filters=filter_dict,
                    canonical_query=semantic_result.canonical_query,
                ),
                input_summary=semantic_result.canonical_query[:120],
            )
            retrieved_docs = [_sanitize_retrieved_doc(r.model_dump()) for r in results]
        except Exception as exc:
            errors.append({"code": "RETRIEVAL_FAILED", "message": "Retrieval failed.", "details": {"error_type": type(exc).__name__}})
            trace.append(_trace_step("retrieval", "failed", input_summary=req.query[:120], error="Retrieval failed."))
    else:
        trace.append(_trace_step("retrieval", "skipped", input_summary="retrieval not required or blocked"))

    trace.append(_trace_step("synthesis", "skipped", output_summary="Natural-language evidence synthesis is not implemented yet."))

    status = "completed"
    message = None
    if intent_result.query_type in ("adversarial", "unanswerable"):
        status = "rejected"
        message = intent_result.rationale
    elif semantic_result.requires_clarification or intent_result.query_type == "ambiguous":
        status = "needs_clarification"
        message = semantic_result.ambiguities[0].reason if semantic_result.ambiguities else intent_result.rationale
    elif errors:
        status = "error"

    trace_dicts = [t.model_dump() | {"step_name": t.stage} for t in trace] if req.include_trace else []
    semantic_dict = semantic_result.to_compat_dict()

    return QueryResponse(
        query=req.query,
        status=status,
        intent=intent_result.model_dump(),
        semantic_mapping=semantic_dict,
        semantic_parse=semantic_result.model_dump(),
        sql_plan=sql_plan.model_dump() if sql_plan else None,
        compiled_queries=[q.model_dump() for q in compiled_queries],
        sql_results=[r.model_dump() for r in sql_results],
        comparison_results=[r.model_dump() for r in comparison_results],
        retrieved_documents=retrieved_docs,
        warnings=warnings,
        errors=errors,
        execution_trace=trace_dicts,
        trace=trace_dicts,
        synthesis_status="not_implemented",
        message=message,
    )


def _run_stage(trace: list[ExecutionTraceStep], stage: str, fn: Callable[[], Any], input_summary: str | None = None) -> Any:
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        result = fn()
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        output_summary = _summarize_result(result)
        trace.append(ExecutionTraceStep(stage=stage, status="completed", started_at=started_at, duration_ms=duration_ms, input_summary=input_summary, output_summary=output_summary))
        return result
    except Exception as exc:
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        trace.append(ExecutionTraceStep(stage=stage, status="failed", started_at=started_at, duration_ms=duration_ms, input_summary=input_summary, error=type(exc).__name__))
        raise


def _trace_step(stage: str, status: str, input_summary: str | None = None, output_summary: str | None = None, error: str | None = None) -> ExecutionTraceStep:
    return ExecutionTraceStep(stage=stage, status=status, started_at=datetime.now(timezone.utc).isoformat(), duration_ms=0.0, input_summary=input_summary, output_summary=output_summary, error=error)


def _summarize_result(result: Any) -> str:
    if isinstance(result, list):
        return f"{len(result)} item(s)"
    if hasattr(result, "query_type"):
        return f"type={result.query_type}"
    if hasattr(result, "specs"):
        return f"{len(result.specs)} spec(s), {len(result.errors)} error(s)"
    if hasattr(result, "row_count"):
        return f"{result.row_count} row(s)"
    if hasattr(result, "canonical_query"):
        return f"metrics={[m.canonical_name for m in result.metrics]}"
    return "completed"


def _sanitize_retrieved_doc(doc: dict[str, Any]) -> dict[str, Any]:
    source_path = doc.get("source_path")
    if source_path:
        normalized = source_path.replace("\\", "/")
        marker = "data/raw/unstructured/"
        if marker in normalized:
            doc["source_path"] = marker + normalized.split(marker, 1)[1]
        else:
            doc["source_path"] = normalized.split("/")[-1]
    return doc
