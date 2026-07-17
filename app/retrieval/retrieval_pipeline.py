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
        canonical_query: str | None = None,
    ) -> list[RetrievedChunk]:
        search_query = canonical_query or query
        expanded_top_k = max(top_k, min(top_k * 4, 50))
        results = self.bm25.retrieve(search_query, top_k=expanded_top_k)
        if not intent_filters and not intent_metrics:
            return results[:top_k]

        scored: list[tuple[float, RetrievedChunk]] = []
        for result in results:
            metadata = result.metadata or {}
            bonus = 0.0
            for key, value in (intent_filters or {}).items():
                metadata_value = metadata.get(key)
                if metadata_value == value:
                    bonus += 5.0
                elif metadata_value in ("All", "Global"):
                    bonus += 0.5
            related_metrics = metadata.get("related_metrics", [])
            for metric in intent_metrics or []:
                if metric in related_metrics:
                    bonus += 2.0
            scored.append((result.score + bonus, result))
        scored.sort(key=lambda item: item[0], reverse=True)
        reranked = []
        for rank, (score, chunk) in enumerate(scored[:top_k], start=1):
            updated = chunk.model_copy(update={"score": round(score, 4), "rank": rank})
            reranked.append(updated)
        return reranked
