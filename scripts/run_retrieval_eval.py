import csv
import json
from datetime import datetime
from pathlib import Path

from app.evaluation.retrieval_eval import run_evaluation


RESULTS_DIR = Path("experiments/results")
REPORTS_DIR = Path("reports")


def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved: {path}")


def save_csv(per_query: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not per_query:
        path.write_text("")
        print(f"Saved (empty): {path}")
        return
    fieldnames = list(per_query[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(per_query)
    print(f"Saved: {path}")


def generate_report(per_query: list[dict], summary: dict) -> str:
    lines = []
    lines.append("# BM25 Retrieval Baseline Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Benchmark size:** {summary['num_queries']} retrieval gold queries")
    lines.append(f"- **Retriever:** BM25 (deterministic, built-in)")
    lines.append(f"- **Top-K evaluated:** 10")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Average Recall@3 | {summary['average_recall_at_3']:.4f} |")
    lines.append(f"| Average Recall@5 | {summary['average_recall_at_5']:.4f} |")
    lines.append(f"| Average Recall@10 | {summary['average_recall_at_10']:.4f} |")
    lines.append(f"| Hit Rate@3 | {summary['hit_rate_at_3']:.4f} |")
    lines.append(f"| Hit Rate@5 | {summary['hit_rate_at_5']:.4f} |")
    lines.append(f"| Hit Rate@10 | {summary['hit_rate_at_10']:.4f} |")
    lines.append(f"| MRR | {summary['mrr']:.4f} |")
    lines.append("")
    lines.append("## Results Table")
    lines.append("")
    lines.append("| ID | Query | Type | Difficulty | Recall@3 | Recall@5 | Recall@10 | Hit@3 | Hit@5 | Hit@10 | RR | Failure |")
    lines.append("|----|-------|------|------------|----------|----------|-----------|-------|-------|--------|----|---------|")
    for r in per_query:
        q_short = r["query"][:50].replace("|", "/")
        lines.append(
            f"| {r['id']} | {q_short} | {r['query_type']} | {r['difficulty']} "
            f"| {r['recall_at_3']:.4f} | {r['recall_at_5']:.4f} | {r['recall_at_10']:.4f} "
            f"| {r['hit_at_3']:.4f} | {r['hit_at_5']:.4f} | {r['hit_at_10']:.4f} "
            f"| {r['reciprocal_rank']:.4f} | {r['failure_reason']} |"
        )
    lines.append("")
    failed = [r for r in per_query if r["failure_reason"] != "no_failure"]
    lines.append("## Failed Cases")
    lines.append("")
    if failed:
        lines.append(f"**{len(failed)} queries** with retrieval failures:")
        lines.append("")
        for r in failed:
            lines.append(f"- **{r['id']}**: {r['query'][:80]}")
            lines.append(f"  - Failure: `{r['failure_reason']}`")
            lines.append(f"  - Expected: {r['expected_docs']}")
            lines.append(f"  - Retrieved (top 10, deduped): {r['retrieved_docs']}")
            lines.append(f"  - Recall@10: {r['recall_at_10']:.4f}")
            lines.append("")
    else:
        lines.append("All queries passed retrieval evaluation.")
        lines.append("")
    lines.append("## Observations")
    lines.append("")
    lines.append("- BM25 provides deterministic, explainable retrieval without external dependencies.")
    lines.append("- The retriever handles definition queries well when query terms overlap with document text.")
    lines.append("- Multi-document queries requiring synthesis across several documents are challenging for BM25 alone.")
    lines.append("- Failure cases typically involve queries where expected documents do not share significant term overlap with the query.")
    lines.append("")
    lines.append("## Known Limitations")
    lines.append("")
    lines.append("- BM25 is purely lexical and cannot capture semantic similarity.")
    lines.append("- Synonyms and business jargon that differ from document terminology cause misses.")
    lines.append("- No query expansion, no relevance feedback, no learning-to-rank.")
    lines.append("- Only 20 documents (120 chunks) in the corpus; results may not generalize to larger corpora.")
    lines.append("- Gold labels are synthetic and may not reflect real-world retrieval difficulty.")
    lines.append("")
    lines.append("## Week 5 Recommendation")
    lines.append("")
    lines.append("Implement vector retrieval (embedding-based) and compare against the BM25 baseline. "
                 "If vector retrieval improves Recall@10 and MRR meaningfully, implement hybrid retrieval "
                 "that combines BM25 and vector scores. Evaluate reranking as a final precision layer.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    print("Running BM25 retrieval evaluation...")
    per_query, summary = run_evaluation()
    print(f"\nEvaluated {summary['num_queries']} queries.")
    print(f"Average Recall@3:  {summary['average_recall_at_3']:.4f}")
    print(f"Average Recall@5:  {summary['average_recall_at_5']:.4f}")
    print(f"Average Recall@10: {summary['average_recall_at_10']:.4f}")
    print(f"Hit Rate@3:        {summary['hit_rate_at_3']:.4f}")
    print(f"Hit Rate@5:        {summary['hit_rate_at_5']:.4f}")
    print(f"Hit Rate@10:       {summary['hit_rate_at_10']:.4f}")
    print(f"MRR:               {summary['mrr']:.4f}")
    save_json({"summary": summary, "per_query": per_query}, RESULTS_DIR / "retrieval_eval_results.json")
    save_csv(per_query, RESULTS_DIR / "retrieval_eval_results.csv")
    report = generate_report(per_query, summary)
    report_path = REPORTS_DIR / "retrieval_baseline_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {report_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()
