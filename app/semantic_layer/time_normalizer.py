import re

from app.schemas.semantic import NormalizedTimeRange, SemanticError
from app.semantic_layer.dimension_registry import get_dimension


QUARTERS = ["Q1_2025", "Q2_2025", "Q3_2025", "Q4_2025"]
LATEST_PERIOD = QUARTERS[-1]


def _period(q_num: str, year: str) -> str:
    return f"Q{q_num}_{year}"


def _period_exists(period: str) -> bool:
    dimension = get_dimension("quarter")
    return bool(dimension and period in dimension.allowed_values)


def normalize_time(query: str, reference_period: str = LATEST_PERIOD) -> tuple[NormalizedTimeRange | None, list[SemanticError]]:
    q_lower = query.lower()
    errors: list[SemanticError] = []

    relative_periods = {
        "this quarter": reference_period,
        "last quarter": reference_period,
        "previous quarter": QUARTERS[max(0, QUARTERS.index(reference_period) - 1)],
    }
    for phrase, period in relative_periods.items():
        if phrase in q_lower:
            return (
                NormalizedTimeRange(
                    periods=[period],
                    start_period=period,
                    end_period=period,
                    reference_period=reference_period,
                    is_relative=True,
                    warnings=[f"Interpreted '{phrase}' relative to latest dataset period {reference_period}."],
                ),
                errors,
            )

    range_match = re.search(r"from\s+q([1-4])\s+(?:\d{4}\s+)?to\s+q([1-4])\s+(\d{4})", q_lower)
    if range_match:
        start_q, end_q, year = range_match.groups()
        start = _period(start_q, year)
        end = _period(end_q, year)
        if start not in QUARTERS or end not in QUARTERS or QUARTERS.index(start) > QUARTERS.index(end):
            return None, [SemanticError(code="INVALID_TIME_RANGE", message="Time range is invalid or reversed.", details={"start_period": start, "end_period": end})]
        periods = QUARTERS[QUARTERS.index(start): QUARTERS.index(end) + 1]
        return NormalizedTimeRange(periods=periods, start_period=start, end_period=end, reference_period=reference_period), errors

    and_match = re.search(r"q([1-4])\s+and\s+q([1-4])\s+(\d{4})", q_lower)
    if and_match:
        q1, q2, year = and_match.groups()
        periods = [_period(q1, year), _period(q2, year)]
        missing = [period for period in periods if not _period_exists(period)]
        if missing:
            errors.append(SemanticError(code="INVALID_TIME_RANGE", message="Requested period is not present in the warehouse.", details={"periods": missing}))
        return NormalizedTimeRange(periods=periods, start_period=periods[0], end_period=periods[-1], reference_period=reference_period), errors

    periods: list[str] = []
    for match in re.finditer(r"\bq([1-4])[_\s-]*(\d{4})\b", q_lower):
        periods.append(_period(match.group(1), match.group(2)))
    for match in re.finditer(r"\b(\d{4})\s*q([1-4])\b", q_lower):
        periods.append(_period(match.group(2), match.group(1)))
    word_patterns = {
        "first": "1",
        "second": "2",
        "third": "3",
        "fourth": "4",
    }
    for word, q_num in word_patterns.items():
        for match in re.finditer(rf"\b{word}\s+quarter\s+of\s+(\d{{4}})\b", q_lower):
            periods.append(_period(q_num, match.group(1)))
    for match in re.finditer(r"\bquarter\s+([1-4])\s+of\s+(\d{4})\b", q_lower):
        periods.append(_period(match.group(1), match.group(2)))

    deduped = []
    for period in periods:
        if period not in deduped:
            deduped.append(period)

    if re.search(r"\bq[1-4]\b", q_lower) and not deduped:
        errors.append(SemanticError(code="MISSING_TIME_PERIOD", message="Quarter was mentioned without an explicit year."))
        return None, errors

    if re.search(r"\byear\s+2025\b|\b2025\b", q_lower) and not deduped and "quarter" not in q_lower:
        return NormalizedTimeRange(grain="year", periods=QUARTERS, start_period=QUARTERS[0], end_period=QUARTERS[-1], reference_period=reference_period), errors

    missing = [period for period in deduped if not _period_exists(period)]
    if missing:
        errors.append(SemanticError(code="INVALID_TIME_RANGE", message="Requested period is not present in the warehouse.", details={"periods": missing}))
    if deduped:
        return NormalizedTimeRange(periods=deduped, start_period=deduped[0], end_period=deduped[-1], reference_period=reference_period), errors
    return None, errors
