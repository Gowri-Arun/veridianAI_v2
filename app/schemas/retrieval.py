from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    text: str
    score: float
    rank: int
    metadata: dict
    source_path: str | None = None
