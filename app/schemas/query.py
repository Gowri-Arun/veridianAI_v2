from pydantic import BaseModel, Field
from typing import Any


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)
    include_trace: bool = True


class QueryResponse(BaseModel):
    query: str
    status: str
    intent: dict[str, Any] | None = None
    semantic_mapping: dict[str, Any] | None = None
    semantic_parse: dict[str, Any] | None = None
    sql_plan: dict[str, Any] | None = None
    compiled_queries: list[dict[str, Any]] = Field(default_factory=list)
    sql_results: list[dict[str, Any]] = Field(default_factory=list)
    comparison_results: list[dict[str, Any]] = Field(default_factory=list)
    retrieved_documents: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[dict[str, Any] | str] = Field(default_factory=list)
    errors: list[dict[str, Any] | str] = Field(default_factory=list)
    execution_trace: list[dict[str, Any]] = Field(default_factory=list)
    trace: list[dict[str, Any]] = Field(default_factory=list)
    synthesis_status: str = "not_implemented"
    message: str | None = None
