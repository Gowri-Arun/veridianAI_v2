from pathlib import Path

from app.retrieval.bm25_retriever import BM25Retriever
from app.schemas.retrieval import RetrievedChunk


DEFAULT_CORPUS_PATH = Path("data/processed/document_chunks.jsonl")


class RetrievalPipeline:
    def __init__(self, corpus_path: Path = DEFAULT_CORPUS_PATH):
        self.bm25 = BM25Retriever(corpus_path=corpus_path)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        intent_metrics: list[str] | None = None,
        intent_filters: dict[str, str] | None = None,
    ) -> list[RetrievedChunk]:
        return self.bm25.retrieve(query, top_k=top_k)
