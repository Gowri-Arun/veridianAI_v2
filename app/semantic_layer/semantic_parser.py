import re
from app.core.patterns import FILTER_PATTERNS
from app.semantic_layer.synonym_mapper import (
    normalize_metric_terms,
    normalize_region,
    normalize_segment,
    normalize_time_period,
    detect_forbidden_confusions,
)


class SemanticParser:
    def parse(self, query: str) -> dict:
        q_lower = query.lower()

        metric_mapped = normalize_metric_terms(query)
        region_mapped = normalize_region(query)
        segment_mapped = normalize_segment(query)
        time_mapped = normalize_time_period(query)

        all_mapped_terms: dict[str, str] = {}
        all_mapped_terms.update(metric_mapped)
        all_mapped_terms.update(region_mapped)
        all_mapped_terms.update(segment_mapped)
        all_mapped_terms.update(time_mapped)

        canonical_parts = _apply_mapped_terms(query, all_mapped_terms)
        canonical_query = " ".join(canonical_parts)

        filters: dict[str, str] = {}
        for pattern, key, value in FILTER_PATTERNS:
            if re.search(pattern, q_lower):
                if key not in filters:
                    filters[key] = value

        metrics = list(set(v for v in metric_mapped.values()))

        warnings = detect_forbidden_confusions(query)

        return {
            "original_query": query,
            "canonical_query": canonical_query,
            "mapped_terms": all_mapped_terms,
            "metrics": metrics,
            "filters": filters,
            "warnings": warnings,
        }


def _apply_mapped_terms(query: str, mapped: dict[str, str]) -> list[str]:
    q_lower = query.lower()
    words = re.findall(r"[a-zA-Z0-9_]+", q_lower)
    resolved = []
    i = 0
    while i < len(words):
        found = False
        for raw_term, canonical in sorted(mapped.items(), key=lambda x: -len(x[0])):
            raw_parts = raw_term.split()
            if i + len(raw_parts) <= len(words):
                candidate = " ".join(words[i : i + len(raw_parts)])
                if candidate == raw_term:
                    resolved.append(canonical)
                    i += len(raw_parts)
                    found = True
                    break
        if not found:
            resolved.append(words[i])
            i += 1
    return resolved
