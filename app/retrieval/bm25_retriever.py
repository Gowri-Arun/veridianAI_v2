import math
import json
import re
from collections import Counter
from pathlib import Path

from app.schemas.retrieval import RetrievedChunk


CORPUS_PATH = Path("data/processed/document_chunks.jsonl")


def _load_corpus(path: Path) -> list[dict]:
    if not path.exists():
        return []
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())


def _compute_idf(corpus: list[str]) -> dict[str, float]:
    n = len(corpus)
    if n == 0:
        return {}
    df: Counter = Counter()
    for doc in corpus:
        terms = set(_tokenize(doc))
        df.update(terms)
    idf: dict[str, float] = {}
    for term, count in df.items():
        idf[term] = math.log(1 + (n - count + 0.5) / (count + 0.5))
    return idf


class BM25Retriever:
    def __init__(self, corpus_path: Path = CORPUS_PATH, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks = _load_corpus(corpus_path)
        self.corpus = [chunk.get("text", "") for chunk in self.chunks]
        self.avg_doc_len = sum(len(_tokenize(d)) for d in self.corpus) / max(len(self.corpus), 1)
        self.idf = _compute_idf(self.corpus)
        self.doc_lengths = [len(_tokenize(d)) for d in self.corpus]

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        query_tokens = _tokenize(query)
        scores = self._score_all(query_tokens)
        ranked_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )
        results = []
        rank = 1
        for idx in ranked_indices[:top_k]:
            if scores[idx] <= 0:
                continue
            chunk = self.chunks[idx]
            results.append(
                RetrievedChunk(
                    chunk_id=chunk.get("chunk_id", f"chunk_{idx}"),
                    doc_id=chunk.get("doc_id", f"doc_{idx}"),
                    title=chunk.get("title", "Untitled"),
                    text=chunk.get("text", ""),
                    score=round(scores[idx], 4),
                    rank=rank,
                    metadata=chunk.get("metadata", {}),
                    source_path=chunk.get("source_path"),
                )
            )
            rank += 1
        return results

    def _score_all(self, query_tokens: list[str]) -> list[float]:
        scores = []
        for i in range(len(self.corpus)):
            scores.append(self._score_doc(query_tokens, i))
        return scores

    def _score_doc(self, query_tokens: list[str], doc_idx: int) -> float:
        doc_len = self.doc_lengths[doc_idx]
        doc_text = self.corpus[doc_idx]
        doc_tokens = _tokenize(doc_text)
        term_freqs = Counter(doc_tokens)
        score = 0.0
        for term in query_tokens:
            if term not in self.idf:
                continue
            tf = term_freqs.get(term, 0)
            idf = self.idf[term]
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
            score += idf * numerator / denominator if denominator > 0 else 0
        return score
