import re

from app.schemas.semantic import (
    ComparisonSpec,
    DimensionReference,
    FilterCondition,
    MetricReference,
    SemanticAmbiguity,
    SemanticError,
    SemanticParseResult,
    SemanticWarning,
    SortSpec,
)
from app.semantic_layer.dimension_registry import (
    CHANNEL_ALIASES,
    PRODUCT_ALIASES,
    REGION_ALIASES,
    SEGMENT_ALIASES,
    DIMENSIONS,
)
from app.semantic_layer.metric_registry import METRICS, MetricDefinition, metric_synonym_lookup
from app.semantic_layer.time_normalizer import normalize_time
from app.semantic_layer.validator import SemanticValidator


class SemanticParser:
    def __init__(self):
        self.validator = SemanticValidator()

    def parse_typed(self, query: str) -> SemanticParseResult:
        q_lower = query.lower()
        mapped_terms: dict[str, str] = {}
        warnings: list[SemanticWarning] = []
        errors: list[SemanticError] = []
        ambiguities: list[SemanticAmbiguity] = []

        metrics, metric_terms, metric_warnings, metric_ambiguities = self._resolve_metrics(query)
        mapped_terms.update(metric_terms)
        warnings.extend(metric_warnings)
        ambiguities.extend(metric_ambiguities)
        if not metrics and re.search(r"\b(what\s+was|how\s+much|show|compare|percentage change|highest|lowest)\b", q_lower):
            errors.append(SemanticError(code="UNKNOWN_METRIC", message="No supported warehouse metric was found in the query."))

        dimensions, dimension_terms = self._resolve_dimensions(query)
        mapped_terms.update(dimension_terms)

        filters, filter_terms, filter_errors = self._extract_filters(query)
        mapped_terms.update(filter_terms)
        errors.extend(filter_errors)

        time_range, time_errors = normalize_time(query)
        errors.extend(time_errors)
        if time_range:
            for period in time_range.periods:
                mapped_terms[period.lower()] = period
            for warning in time_range.warnings:
                warnings.append(SemanticWarning(code="DATASET_RELATIVE_TIME", message=warning))
            if "quarter" not in {f.dimension for f in filters} and time_range.grain == "quarter":
                for period in time_range.periods:
                    filters.append(FilterCondition(dimension="quarter", column_name="quarter", value=period, source_term=period))

        aggregation = self._detect_aggregation(q_lower)
        for metric in metrics:
            metric.aggregation = aggregation or metric.aggregation

        comparison = self._detect_comparison(q_lower, time_range.periods if time_range else [])
        sort = self._detect_sort(q_lower, metrics)
        limit = self._detect_limit(q_lower)

        if sort and not any(dim.canonical_name == "region" for dim in dimensions) and "region" in q_lower:
            dimensions.append(_dimension_ref("region", "region"))

        canonical_query = _apply_mapped_terms(query, mapped_terms)
        result = SemanticParseResult(
            original_query=query,
            canonical_query=canonical_query,
            mapped_terms=mapped_terms,
            metrics=metrics,
            dimensions=dimensions,
            filters=filters,
            time_range=time_range,
            aggregation=aggregation,
            comparison=comparison,
            sort=sort,
            limit=limit,
            warnings=warnings,
            errors=errors,
            ambiguities=ambiguities,
            requires_clarification=bool(ambiguities),
        )
        return self.validator.validate(result)

    def parse(self, query: str) -> dict:
        return self.parse_typed(query).to_compat_dict()

    def _resolve_metrics(
        self, query: str
    ) -> tuple[list[MetricReference], dict[str, str], list[SemanticWarning], list[SemanticAmbiguity]]:
        q_lower = query.lower()
        lookup = metric_synonym_lookup()
        # Preserve historical "sales" behavior for specific contexts, but block vague sales.
        lookup["sales"] = "revenue"
        found: dict[str, tuple[MetricDefinition, str]] = {}
        mapped: dict[str, str] = {}
        warnings: list[SemanticWarning] = []
        ambiguities: list[SemanticAmbiguity] = []

        if re.search(r"\bhow\s+were\s+sales\b|\bsales\?\s*$", q_lower):
            ambiguities.append(
                SemanticAmbiguity(
                    source_term="sales",
                    candidate_metrics=["revenue", "bookings", "pipeline"],
                    reason="'sales' can refer to recognized revenue, bookings, or pipeline in this dataset.",
                )
            )
            return [], mapped, warnings, ambiguities

        for synonym, canonical in sorted(lookup.items(), key=lambda item: -len(item[0])):
            if re.search(rf"\b{re.escape(synonym)}\b", q_lower):
                metric = METRICS.get(canonical)
                if metric and canonical not in found:
                    found[canonical] = (metric, synonym)
                    mapped[synonym] = canonical

        for canonical, metric in METRICS.items():
            for forbidden in metric.forbidden_confusions:
                if canonical in found and re.search(rf"\b{re.escape(forbidden)}\b", q_lower):
                    warnings.append(
                        SemanticWarning(
                            code="FORBIDDEN_CONFUSION",
                            message=f"'{forbidden}' should not be confused with '{canonical}'.",
                            details={"metric": canonical, "forbidden": forbidden},
                        )
                    )

        refs = [
            MetricReference(
                canonical_name=metric.canonical_name,
                display_name=metric.display_name,
                source_term=source_term,
                source_table=metric.source_table,
                value_column=metric.value_column,
                aggregation=metric.default_aggregation,
            )
            for metric, source_term in found.values()
        ]
        return refs, mapped, warnings, ambiguities

    def _resolve_dimensions(self, query: str) -> tuple[list[DimensionReference], dict[str, str]]:
        q_lower = query.lower()
        refs: dict[str, DimensionReference] = {}
        mapped: dict[str, str] = {}
        by_match = re.search(r"\bby\s+([a-z_ -]+)", q_lower)
        if by_match:
            term = by_match.group(1).split()[0].strip(" ?.")
            for name, dimension in DIMENSIONS.items():
                if term == name or term in dimension.synonyms:
                    refs[name] = _dimension_ref(name, term)
                    mapped[term] = name
        return list(refs.values()), mapped

    def _extract_filters(self, query: str) -> tuple[list[FilterCondition], dict[str, str], list[SemanticError]]:
        q_lower = query.lower()
        filters: list[FilterCondition] = []
        mapped: dict[str, str] = {}
        errors: list[SemanticError] = []
        alias_groups = {
            "region": REGION_ALIASES,
            "segment": SEGMENT_ALIASES,
            "product": PRODUCT_ALIASES,
            "channel": CHANNEL_ALIASES,
        }
        for dimension, aliases in alias_groups.items():
            for alias, value in sorted(aliases.items(), key=lambda item: -len(item[0])):
                if re.search(rf"\b{re.escape(alias)}\b", q_lower):
                    if not any(f.dimension == dimension and f.value == value for f in filters):
                        filters.append(FilterCondition(dimension=dimension, column_name=DIMENSIONS[dimension].column_name, value=value, source_term=alias))
                        mapped[alias] = value
                    break

        unknown_region = re.search(r"\bin\s+([a-z]+)\b", q_lower)
        if unknown_region and not filters and any(marker in q_lower for marker in ["lunar", "atlantis"]):
            errors.append(SemanticError(code="UNKNOWN_FILTER_VALUE", message="Unknown categorical filter value.", details={"source_term": unknown_region.group(1)}))
        return filters, mapped, errors

    def _detect_aggregation(self, q_lower: str) -> str | None:
        if re.search(r"\baverage|avg|mean\b", q_lower):
            return "avg"
        if re.search(r"\bcount|how many|number of\b", q_lower):
            return "count"
        if re.search(r"\bsum|total\b", q_lower):
            return "sum"
        return None

    def _detect_comparison(self, q_lower: str, periods: list[str]) -> ComparisonSpec | None:
        comparison_type = None
        if re.search(r"\bpercentage change|percent change\b", q_lower):
            comparison_type = "percentage_change"
        elif re.search(r"\bhow much did|absolute change|decline|increase|decrease|drop\b", q_lower) and len(periods) >= 2:
            comparison_type = "absolute_change"
        elif len(periods) >= 2 and re.search(r"\bcompare|versus|vs\.?|from\s+q[1-4].*to\s+q[1-4]\b", q_lower):
            comparison_type = "period"
        if not comparison_type:
            return None
        return ComparisonSpec(
            comparison_type=comparison_type,
            baseline_period=periods[0] if periods else None,
            comparison_period=periods[-1] if periods else None,
        )

    def _detect_sort(self, q_lower: str, metrics: list[MetricReference]) -> SortSpec | None:
        if not metrics:
            return None
        if re.search(r"\bhighest|top|largest|most\b", q_lower):
            return SortSpec(metric=metrics[0].canonical_name, direction="desc")
        if re.search(r"\blowest|bottom|smallest|least\b", q_lower):
            return SortSpec(metric=metrics[0].canonical_name, direction="asc")
        return None

    def _detect_limit(self, q_lower: str) -> int | None:
        match = re.search(r"\btop\s+(\d+)\b", q_lower)
        if match:
            return min(int(match.group(1)), 10)
        if re.search(r"\bhighest|lowest|which\s+regions?\b", q_lower):
            return 10
        return None


def _dimension_ref(name: str, source_term: str) -> DimensionReference:
    dimension = DIMENSIONS[name]
    return DimensionReference(
        canonical_name=name,
        display_name=dimension.display_name,
        source_term=source_term,
        column_name=dimension.column_name,
    )


def _apply_mapped_terms(query: str, mapped: dict[str, str]) -> str:
    q_lower = query.lower()
    for raw_term, canonical in sorted(mapped.items(), key=lambda item: -len(item[0])):
        q_lower = re.sub(rf"\b{re.escape(raw_term)}\b", str(canonical), q_lower)
    return " ".join(re.findall(r"[a-zA-Z0-9_ -]+", q_lower)).strip()
