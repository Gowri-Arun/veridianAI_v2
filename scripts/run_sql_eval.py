import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess

from app.evaluation.sql_eval import difficulty_distribution, category_distribution, run_evaluation
from scripts.validate_sql_benchmark import DEFAULT_PATH, load_cases


RESULTS_DIR = Path("experiments/results")
REPORTS_DIR = Path("reports")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category")
    parser.add_argument("--difficulty")
    parser.add_argument("--case-id")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    cases = load_cases(DEFAULT_PATH)
    results, summary = run_evaluation(
        DEFAULT_PATH,
        category=args.category,
        difficulty=args.difficulty,
        case_id=args.case_id,
        fail_fast=args.fail_fast,
    )
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_path": str(DEFAULT_PATH),
        "commit": _commit_hash(),
        "summary": summary.model_dump(mode="json"),
        "results": [result.model_dump(mode="json") for result in results],
    }
    json_path = RESULTS_DIR / "sql_eval_results.json"
    csv_path = RESULTS_DIR / "sql_eval_results.csv"
    report_path = REPORTS_DIR / "sql_benchmark_report.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_csv(results, csv_path)
    report_path.write_text(_render_report(cases, results, summary), encoding="utf-8")

    print(f"SQL benchmark cases evaluated: {summary.total_cases}")
    print(f"Passed: {summary.passed_cases} | Failed: {summary.failed_cases}")
    print(f"Overall case accuracy: {summary.metrics.get('overall_case_accuracy', 0):.4f}")
    print(f"Saved: {json_path}")
    print(f"Saved: {csv_path}")
    print(f"Saved: {report_path}")


def _write_csv(results, path: Path) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "category", "difficulty", "status", "executed_sql_count", "row_count", "failure_categories"])
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "case_id": result.case_id,
                    "category": result.category,
                    "difficulty": result.difficulty,
                    "status": result.status,
                    "executed_sql_count": result.executed_sql_count,
                    "row_count": result.row_count,
                    "failure_categories": ";".join(f.failure_category for f in result.failures),
                }
            )


def _render_report(cases, results, summary) -> str:
    failed = [result for result in results if result.status != "passed"]
    lines = [
        "# SQL Benchmark Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Repository commit: {_commit_hash()}",
        f"Benchmark cases: {len(results)}",
        "",
        "## Distribution",
        "",
        f"Category distribution: `{category_distribution(cases)}`",
        f"Difficulty distribution: `{difficulty_distribution(cases)}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for name, value in summary.metrics.items():
        lines.append(f"| {name} | {value:.4f} |")
    lines.extend(
        [
            "",
            "## Failure Categories",
            "",
            f"`{summary.failure_category_counts}`",
            "",
            "## Failed Cases",
            "",
        ]
    )
    if failed:
        for result in failed:
            lines.append(f"- `{result.case_id}`: {', '.join(f.failure_category for f in result.failures)}")
    else:
        lines.append("No failed cases.")
    lines.extend(
        [
            "",
            "## Known Limitations",
            "",
            "- The benchmark evaluates deterministic SQL semantics, not answer synthesis.",
            "- Expected numeric rows are intentionally bounded to stable row-count/column/comparison checks unless materialized by a trusted reference path.",
            "- No LLM-as-judge is used.",
        ]
    )
    return "\n".join(lines)


def _commit_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


if __name__ == "__main__":
    main()
