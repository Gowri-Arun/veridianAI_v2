from pydantic import BaseModel, Field
from typing import Any


class TraceStep(BaseModel):
    step_name: str
    status: str
    input_summary: str | None = None
    output_summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionTraceStep(BaseModel):
    stage: str
    status: str
    started_at: str
    duration_ms: float | None = None
    input_summary: str | None = None
    output_summary: str | None = None
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None

    @property
    def step_name(self) -> str:
        return self.stage
