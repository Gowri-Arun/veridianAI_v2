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
    retrieved_documents: list[dict[str, Any]] = []
    trace: list[dict[str, Any]] = []
    message: str | None = None
