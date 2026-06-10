from pydantic import BaseModel, Field
from typing import Literal

QueryType = Literal[
    "simple_document",
    "simple_sql",
    "metric_lookup",
    "comparison",
    "trend_analysis",
    "hybrid_sql_document",
    "root_cause_analysis",
    "ambiguous",
    "unanswerable",
    "contradiction",
    "adversarial",
]


class IntentClassification(BaseModel):
    query_type: QueryType
    confidence: float = Field(ge=0.0, le=1.0)
    metrics: list[str] = []
    dimensions: list[str] = []
    filters: dict[str, str] = {}
    requires_retrieval: bool = False
    requires_sql: bool = False
    requires_clarification: bool = False
    rationale: str
