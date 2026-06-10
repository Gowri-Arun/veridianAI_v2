from pydantic import BaseModel
from typing import Any


class TraceStep(BaseModel):
    step_name: str
    status: str
    input_summary: str | None = None
    output_summary: str | None = None
    metadata: dict[str, Any] = {}
