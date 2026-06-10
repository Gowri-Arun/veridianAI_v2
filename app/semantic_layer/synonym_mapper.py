import re

METRIC_SYNONYMS: dict[str, str] = {
    "sales": "revenue",
    "income": "revenue",
    "recognized revenue": "revenue",
    "revenue": "revenue",
    "ad spend": "marketing_spend",
    "ads": "marketing_spend",
    "marketing spend": "marketing_spend",
    "marketing": "marketing_spend",
    "customer loss": "churn",
    "lost customers": "churn",
    "churn": "churn",
    "attrition": "churn",
    "support issues": "support_tickets",
    "support tickets": "support_tickets",
    "escalations": "support_tickets",
    "usage": "product_usage",
    "product usage": "product_usage",
    "pipeline": "sales_pipeline",
    "sales pipeline": "sales_pipeline",
}

SEGMENT_SYNONYMS: dict[str, str] = {
    "enterprise clients": "Enterprise",
    "enterprise customers": "Enterprise",
    "large customers": "Enterprise",
    "enterprise": "Enterprise",
    "smb": "SMB",
    "small businesses": "SMB",
    "small business": "SMB",
    "mid-market": "Mid-Market",
    "midmarket": "Mid-Market",
    "mid market": "Mid-Market",
}

REGION_SYNONYMS: dict[str, str] = {
    "apac": "APAC",
    "asia-pacific": "APAC",
    "asia pacific": "APAC",
    "emea": "EMEA",
    "europe": "EMEA",
    "north america": "North America",
    "na": "North America",
    "latam": "LATAM",
}

TIME_SYNONYMS: dict[str, str] = {
    "q1": "Q1_2025",
    "q2": "Q2_2025",
    "q3": "Q3_2025",
    "q4": "Q4_2025",
    "last quarter": "Q4_2025",
    "previous quarter": "Q3_2025",
}

FORBIDDEN_CONFUSIONS: dict[str, list[str]] = {
    "revenue": ["bookings", "pipeline", "sales_pipeline"],
    "churn": ["support_tickets"],
    "marketing_spend": ["cac", "customer_acquisition_cost"],
}


def _build_lookup(synonym_map: dict[str, str]) -> list[tuple[str, str]]:
    sorted_terms = sorted(synonym_map.keys(), key=len, reverse=True)
    return [(re.escape(t), synonym_map[t]) for t in sorted_terms]


_METRIC_LOOKUP = _build_lookup(METRIC_SYNONYMS)
_SEGMENT_LOOKUP = _build_lookup(SEGMENT_SYNONYMS)
_REGION_LOOKUP = _build_lookup(REGION_SYNONYMS)
_TIME_LOOKUP = _build_lookup(TIME_SYNONYMS)


def normalize_metric_terms(query: str) -> dict[str, str]:
    q_lower = query.lower()
    mapped: dict[str, str] = {}
    for pattern, canonical in _METRIC_LOOKUP:
        if re.search(pattern, q_lower):
            key = q_lower[re.search(pattern, q_lower).start():re.search(pattern, q_lower).end()]
            mapped[key.strip()] = canonical
    return mapped


def normalize_region(query: str) -> dict[str, str]:
    q_lower = query.lower()
    mapped: dict[str, str] = {}
    for pattern, canonical in _REGION_LOOKUP:
        if re.search(pattern, q_lower):
            key = q_lower[re.search(pattern, q_lower).start():re.search(pattern, q_lower).end()]
            mapped[key.strip()] = canonical
    return mapped


def normalize_segment(query: str) -> dict[str, str]:
    q_lower = query.lower()
    mapped: dict[str, str] = {}
    for pattern, canonical in _SEGMENT_LOOKUP:
        if re.search(pattern, q_lower):
            key = q_lower[re.search(pattern, q_lower).start():re.search(pattern, q_lower).end()]
            mapped[key.strip()] = canonical
    return mapped


def normalize_time_period(query: str) -> dict[str, str]:
    q_lower = query.lower()
    mapped: dict[str, str] = {}
    for pattern, canonical in _TIME_LOOKUP:
        if re.search(pattern, q_lower):
            key = q_lower[re.search(pattern, q_lower).start():re.search(pattern, q_lower).end()]
            mapped[key.strip()] = canonical
    return mapped


def detect_forbidden_confusions(query: str) -> list[str]:
    q_lower = query.lower()
    warnings: list[str] = []
    for canonical, forbidden_list in FORBIDDEN_CONFUSIONS.items():
        has_canonical = canonical in q_lower or any(
            s.lower() in q_lower for s in METRIC_SYNONYMS if METRIC_SYNONYMS[s] == canonical
        )
        for forbidden in forbidden_list:
            if has_canonical and forbidden in q_lower:
                warnings.append(
                    f"'{forbidden}' should not be confused with '{canonical}'"
                )
    return warnings
