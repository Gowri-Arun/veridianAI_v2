from app.semantic_layer.time_normalizer import normalize_time


def periods(text: str):
    result, errors = normalize_time(text)
    assert not errors
    assert result is not None
    return result.periods


def test_q4_2025_formats():
    assert periods("Q4 2025") == ["Q4_2025"]
    assert periods("Q4_2025") == ["Q4_2025"]
    assert periods("2025 Q4") == ["Q4_2025"]
    assert periods("fourth quarter of 2025") == ["Q4_2025"]
    assert periods("quarter 4 of 2025") == ["Q4_2025"]


def test_two_periods_and_range():
    assert periods("Q3 and Q4 2025") == ["Q3_2025", "Q4_2025"]
    assert periods("from Q3 to Q4 2025") == ["Q3_2025", "Q4_2025"]


def test_last_quarter_dataset_relative():
    result, errors = normalize_time("last quarter")
    assert not errors
    assert result is not None
    assert result.periods == ["Q4_2025"]
    assert result.is_relative is True
    assert result.reference_period == "Q4_2025"


def test_invalid_quarter_missing_year():
    result, errors = normalize_time("Q4 performance")
    assert result is None
    assert errors[0].code == "MISSING_TIME_PERIOD"


def test_reversed_range():
    result, errors = normalize_time("from Q4 to Q3 2025")
    assert result is None
    assert errors[0].code == "INVALID_TIME_RANGE"


def test_period_not_present():
    result, errors = normalize_time("Q4 2026")
    assert result is not None
    assert errors[0].code == "INVALID_TIME_RANGE"
