from collections import Counter
from pathlib import Path
from typing import Any

from app.agents.intent_agent import IntentAgent
from app.evaluation.sql_metrics import summarize_results
from app.schemas.benchmark import BenchmarkCaseResult, BenchmarkFailure, SQLBenchmarkCase
from app.semantic_layer.semantic_parser import SemanticParser
from app.sql_engine.comparison import calculate_comparison
from app.sql_engine.compiler import SQLCompiler
from app.sql_engine.executor import DuckDBExecutor
from app.sql_engine.planner import StructuredQueryPlanner
from app.sql_engine.safety import SQLSafetyValidator
from scripts.validate_sql_benchmark import DEFAULT_PATH, load_cases


class SQLBenchmarkEvaluator:
    def __init__(self):
        self.intent = IntentAgent()
        self.parser = SemanticParser()
        self.planner = StructuredQueryPlanner()
        self.compiler = SQLCompiler()
        self.safety = SQLSafetyValidator()
        self.executor = DuckDBExecutor()

    def evaluate_case(self, case: SQLBenchmarkCase) -> BenchmarkCaseResult:
        checks: dict[str, bool] = {}
        failures: list[BenchmarkFailure] = []
        executed_sql_count = 0
        row_count = 0
        try:
            intent = self.intent.classify(case.question)
            semantic = self.parser.parse_typed(case.question)
            metric_names = [m.canonical_name for m in semantic.metrics]
            dimension_names = [d.canonical_name for d in semantic.dimensions]
            filters = {f.dimension: f.value for f in semantic.filters}
            periods = semantic.time_range.periods if semantic.time_range else []
            semantic_ok = not semantic.errors and not semantic.requires_clarification

            if case.expected_behavior == "requires_clarification":
                ok = semantic.requires_clarification or intent.requires_clarification
                checks["clarification_accuracy"] = ok
                if not ok:
                    failures.append(_failure(case, "EXPECTED_CLARIFICATION_FAILED", "semantic", True, False))
                checks["adversarial_block_rate"] = True if case.category != "adversarial" else executed_sql_count == 0
                return _result(case, checks, failures, executed_sql_count, row_count)

            if case.expected_behavior == "reject":
                ok = intent.query_type == "adversarial"
                checks["adversarial_block_rate"] = executed_sql_count == 0 and ok
                if not ok:
                    failures.append(_failure(case, "EXPECTED_REJECTION_FAILED", "intent", "adversarial", intent.query_type))
                return _result(case, checks, failures, executed_sql_count, row_count)

            if case.expected_behavior == "unsupported":
                plan = self.planner.plan(semantic)
                ok = bool(semantic.errors or semantic.requires_clarification or plan.errors or not plan.specs)
                checks["unsupported_rejection_accuracy"] = ok
                if not ok:
                    failures.append(_failure(case, "UNSUPPORTED_QUERY_EXECUTED", "planning", "blocked", "planned"))
                return _result(case, checks, failures, executed_sql_count, row_count)

            checks["semantic_parse_accuracy"] = semantic_ok
            _check(case, checks, failures, "metric_selection_accuracy", set(case.expected_metrics), set(metric_names), "METRIC_RESOLUTION_ERROR", "semantic")
            _check(case, checks, failures, "dimension_selection_accuracy", set(case.expected_dimensions), set(dimension_names), "DIMENSION_RESOLUTION_ERROR", "semantic")
            _check(case, checks, failures, "filter_accuracy", case.expected_filters, {k: filters.get(k) for k in case.expected_filters}, "FILTER_EXTRACTION_ERROR", "semantic")
            _check(case, checks, failures, "period_accuracy", case.expected_periods, periods, "TIME_NORMALIZATION_ERROR", "semantic")

            plan = self.planner.plan(semantic)
            specs = plan.specs
            shapes = [s.query_shape for s in specs]
            if case.expected_query_shape:
                _check(case, checks, failures, "query_shape_accuracy", case.expected_query_shape, shapes[0] if shapes else None, "QUERY_SHAPE_ERROR", "planning")
            _check(case, checks, failures, "table_selection_accuracy", set(case.expected_tables), set(s.source_table for s in specs), "TABLE_SELECTION_ERROR", "planning")
            _check(case, checks, failures, "column_selection_accuracy", set(case.expected_value_columns), set(s.value_column for s in specs), "COLUMN_SELECTION_ERROR", "planning")
            if case.expected_aggregation:
                _check(case, checks, failures, "aggregation_accuracy", case.expected_aggregation, specs[0].aggregation if specs else None, "AGGREGATION_ERROR", "planning")
            if case.expected_dimensions:
                _check(case, checks, failures, "grouping_accuracy", set(case.expected_dimensions), set(specs[0].dimensions if specs else []), "GROUPING_ERROR", "planning")

            result_ok = True
            comparison_ok = True
            execution_ok = bool(specs) and not plan.errors
            for spec in specs:
                compiled = self.compiler.compile(spec)
                if any(str(param) in compiled.sql for param in compiled.parameters):
                    failures.append(_failure(case, "PARAMETERIZATION_ERROR", "compilation", "parameter placeholders", compiled.sql))
                safety_error = self.safety.validate(compiled)
                if safety_error:
                    execution_ok = False
                    failures.append(_failure(case, "SQL_SAFETY_ERROR", "safety", None, safety_error.message))
                    continue
                execution = self.executor.execute(compiled)
                executed_sql_count += 1
                row_count += execution.row_count
                if execution.error:
                    execution_ok = False
                    failures.append(_failure(case, "EXECUTION_ERROR", "execution", None, execution.error.message))
                    continue
                expected_cols = case.expected_result.columns
                if expected_cols and not set(expected_cols).issubset(set(execution.columns)):
                    result_ok = False
                    failures.append(_failure(case, "COLUMN_SELECTION_ERROR", "execution", expected_cols, execution.columns))
                if case.expected_result.row_count is not None and len(specs) == 1 and execution.row_count != case.expected_result.row_count:
                    result_ok = False
                    failures.append(_failure(case, "EMPTY_RESULT_ERROR", "execution", case.expected_result.row_count, execution.row_count))
                comparison = calculate_comparison(spec, execution)
                if comparison and case.expected_result.comparison_direction:
                    if comparison.direction != case.expected_result.comparison_direction:
                        comparison_ok = False
                        failures.append(_failure(case, "COMPARISON_CALCULATION_ERROR", "comparison", case.expected_result.comparison_direction, comparison.direction))
            checks["execution_success_rate"] = execution_ok
            checks["result_accuracy"] = result_ok
            if case.category in {"absolute_change", "percentage_change"}:
                checks["comparison_accuracy"] = comparison_ok
            checks["overall_case_accuracy"] = not failures and all(checks.values())
            return _result(case, checks, failures, executed_sql_count, row_count)
        except Exception as exc:
            failures.append(BenchmarkFailure(case_id=case.id, failure_category="UNEXPECTED_INTERNAL_ERROR", stage="internal", message=str(exc), expected=None, actual=type(exc).__name__))
            return BenchmarkCaseResult(case_id=case.id, category=case.category, difficulty=case.difficulty, status="error", checks=checks, failures=failures, executed_sql_count=executed_sql_count, row_count=row_count)

    def run(self, cases: list[SQLBenchmarkCase]) -> tuple[list[BenchmarkCaseResult], Any]:
        results = [self.evaluate_case(case) for case in cases]
        return results, summarize_results(results)


def run_evaluation(
    benchmark_path: Path = DEFAULT_PATH,
    category: str | None = None,
    difficulty: str | None = None,
    case_id: str | None = None,
    fail_fast: bool = False,
):
    cases = load_cases(benchmark_path)
    if category:
        cases = [case for case in cases if case.category == category]
    if difficulty:
        cases = [case for case in cases if case.difficulty == difficulty]
    if case_id:
        cases = [case for case in cases if case.id == case_id]
    evaluator = SQLBenchmarkEvaluator()
    results = []
    for case in cases:
        result = evaluator.evaluate_case(case)
        results.append(result)
        if fail_fast and result.status != "passed":
            break
    return results, summarize_results(results)


def category_distribution(cases: list[SQLBenchmarkCase]) -> dict[str, int]:
    return dict(Counter(case.category for case in cases))


def difficulty_distribution(cases: list[SQLBenchmarkCase]) -> dict[str, int]:
    return dict(Counter(case.difficulty for case in cases))


def _check(case, checks, failures, check_name, expected, actual, failure_category, stage):
    ok = expected == actual
    checks[check_name] = ok
    if not ok:
        failures.append(_failure(case, failure_category, stage, expected, actual))


def _failure(case, category, stage, expected, actual):
    return BenchmarkFailure(case_id=case.id, failure_category=category, stage=stage, message=f"{stage} expectation failed", expected=expected, actual=actual)


def _result(case, checks, failures, executed_sql_count, row_count):
    if "overall_case_accuracy" not in checks:
        checks["overall_case_accuracy"] = not failures and all(checks.values())
    return BenchmarkCaseResult(
        case_id=case.id,
        category=case.category,
        difficulty=case.difficulty,
        status="passed" if checks["overall_case_accuracy"] else "failed",
        checks=checks,
        failures=failures,
        executed_sql_count=executed_sql_count,
        row_count=row_count,
    )
