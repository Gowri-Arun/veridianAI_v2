import re
from app.core.patterns import FILTER_PATTERNS
from app.schemas.intent import IntentClassification, QueryType


METRIC_PATTERNS: list[tuple[str, str]] = [
    (r"\brevenue\b|\brecognized revenue\b|\bsales\b|\bincome\b", "revenue"),
    (r"\bmarketing spend\b|\bad spend\b|\bads\b|\bmarketing\b", "marketing_spend"),
    (r"\bchurn\b|\bcustomer loss\b|\blost customers\b|\battrition\b", "churn"),
    (r"\bsupport tickets?\b|\bescalations?\b|\bsupport issues?\b", "support_tickets"),
    (r"\bproduct usage\b|\busage\b", "product_usage"),
    (r"\bpipeline\b|\bsales pipeline\b", "sales_pipeline"),
    (r"\bdiscount\b|\bpricing?\b", "pricing"),
]

DIMENSION_PATTERNS: list[tuple[str, str]] = [
    (r"\bregion\b|\bgeography\b|\bgeo\b", "region"),
    (r"\bsegment\b|\bcustomer segment\b|\bseg\b", "segment"),
    (r"\bproduct\b", "product"),
    (r"\bquarter\b|\bq[1-4]\b", "quarter"),
    (r"\bchannel\b", "channel"),
]

ADVERSARIAL_PATTERNS = [
    r"ignore\s+(previous|all|the).*rules",
    r"drop\s+table",
    r"delete\s+(from\s+)?\w+",
    r"show\s+(secrets?|keys?|passwords?)",
    r"reveal\s+(api\s*)?key",
    r"bypass\s+(restrictions?|safeguards?)",
]


class IntentAgent:
    def classify(self, query: str) -> IntentClassification:
        q_lower = query.lower().strip()

        if not q_lower or len(q_lower) < 3:
            return IntentClassification(
                query_type="ambiguous",
                confidence=0.95,
                rationale="Query is too short to classify meaningfully.",
                requires_clarification=True,
            )

        has_adversarial = any(re.search(p, q_lower) for p in ADVERSARIAL_PATTERNS)
        if has_adversarial:
            return IntentClassification(
                query_type="adversarial",
                confidence=0.95,
                rationale="Query matches known adversarial or injection patterns.",
            )

        has_unanswerable_blame = re.search(
            r"\b(which|who)\s+\w+\s+(caused|is responsible|is to blame|made|dropped|lost)\b",
            q_lower,
        )
        has_unanswerable_attribution = re.search(
            r"\b(which|who)\s+(manager|person|employee|team|rep|salesperson)\b", q_lower
        )
        if has_unanswerable_blame or has_unanswerable_attribution:
            return IntentClassification(
                query_type="unanswerable",
                confidence=0.88,
                rationale="Query asks about unanswerable attribution to a specific individual.",
                requires_clarification=True,
            )

        has_contradiction = re.search(
            r"\b(contradict|contradiction|inconsistent|conflict|disagree|but\s+also)\b",
            q_lower,
        )
        if has_contradiction and not re.search(r"\b(why|cause|reason)\b", q_lower):
            return IntentClassification(
                query_type="contradiction",
                confidence=0.80,
                rationale="Query signals contradictory or inconsistent information.",
                requires_retrieval=True,
            )

        has_vague = not re.search(
            r"\b(apac|emea|north america|latam|enterprise|smb|q[1-4]|revenue|churn)\b",
            q_lower,
        )
        is_ambiguous_pattern = re.search(
            r"\b(drop|decline|decrease|increase|why\s+did|what\s+happened|tell\s+me\s+about)\b",
            q_lower,
        )
        if has_vague and is_ambiguous_pattern:
            return IntentClassification(
                query_type="ambiguous",
                confidence=0.78,
                rationale="Query is vague without specific region, segment, or metric context.",
                requires_clarification=True,
            )

        metrics = self._extract_metrics(q_lower)
        filters = self._extract_filters(q_lower)
        dimensions = self._extract_dimensions(q_lower)

        has_comparison = re.search(
            r"\b(compare|versus|vs\.?|between|difference\s+between|differ\b|relative\b)\b",
            q_lower,
        )
        has_trend = re.search(
            r"\b(trend|increase|decrease|decline|drop|growth|changed?\s+over\s+time|over\s+the\s+(quarter|year|period)|trajectory)\b",
            q_lower,
        )
        has_root_cause = re.search(
            r"\b(why|cause|reason|driven\s+by|explain|despite|root\s+cause|because)\b",
            q_lower,
        )
        has_document = re.search(
            r"\b(what\s+is|define|definition|explain\s+metric|difference\s+between\s+\w+\s+and\s+\w+|describe|summarize)\b",
            q_lower,
        )
        has_sql = re.search(
            r"\b(what\s+was|how\s+much|total|average|sum|count|revenue\s+in|churn\s+in|spend\s+in)\b",
            q_lower,
        )

        has_hybrid = has_root_cause and len(filters) >= 2
        has_adversarial_secondary = re.search(r"\bignore\b|\boverride\b", q_lower)

        if has_adversarial_secondary:
            return IntentClassification(
                query_type="adversarial",
                confidence=0.90,
                rationale="Query contains override or ignore keywords.",
                metrics=metrics,
                dimensions=dimensions,
                filters=filters,
            )

        if has_root_cause and has_comparison:
            return IntentClassification(
                query_type="root_cause_analysis",
                confidence=0.90,
                rationale="Query asks for causal explanation with comparison.",
                metrics=metrics,
                dimensions=dimensions,
                filters=filters,
                requires_retrieval=True,
                requires_sql=True,
            )

        if has_root_cause and has_trend:
            return IntentClassification(
                query_type="root_cause_analysis",
                confidence=0.87,
                rationale="Query asks for root cause with trend context.",
                metrics=metrics,
                dimensions=dimensions,
                filters=filters,
                requires_retrieval=True,
                requires_sql=True,
            )

        if has_root_cause:
            has_specific_metric = bool(metrics)
            return IntentClassification(
                query_type="root_cause_analysis",
                confidence=0.84,
                rationale="Query asks for causal explanation.",
                metrics=metrics,
                dimensions=dimensions,
                filters=filters,
                requires_retrieval=True,
                requires_sql=has_specific_metric,
            )

        if has_trend and has_comparison:
            return IntentClassification(
                query_type="comparison",
                confidence=0.88,
                rationale="Query asks to compare trends.",
                metrics=metrics,
                dimensions=dimensions,
                filters=filters,
                requires_retrieval=True,
                requires_sql=True,
            )

        if has_comparison:
            return IntentClassification(
                query_type="comparison",
                confidence=0.86,
                rationale="Query asks for comparison between entities.",
                metrics=metrics,
                dimensions=dimensions,
                filters=filters,
                requires_retrieval=True,
                requires_sql=True,
            )

        if has_trend:
            return IntentClassification(
                query_type="trend_analysis",
                confidence=0.85,
                rationale="Query asks for trend or change over time.",
                metrics=metrics,
                dimensions=dimensions,
                filters=filters,
                requires_retrieval=True,
                requires_sql=True,
            )

        if has_document and has_sql:
            return IntentClassification(
                query_type="hybrid_sql_document",
                confidence=0.80,
                rationale="Query requires both document and SQL evidence.",
                metrics=metrics,
                dimensions=dimensions,
                filters=filters,
                requires_retrieval=True,
                requires_sql=True,
            )

        if has_document:
            return IntentClassification(
                query_type="simple_document",
                confidence=0.85,
                rationale="Query asks for definition or explanation from documents.",
                metrics=metrics,
                dimensions=dimensions,
                filters=filters,
                requires_retrieval=True,
                requires_sql=False,
            )

        if has_sql or metrics:
            has_metric_lookup_only = (
                bool(metrics)
                and not has_trend
                and not has_comparison
                and not has_root_cause
            )
            if has_metric_lookup_only:
                return IntentClassification(
                    query_type="metric_lookup",
                    confidence=0.82,
                    rationale="Query looks up a specific metric value.",
                    metrics=metrics,
                    dimensions=dimensions,
                    filters=filters,
                    requires_retrieval=False,
                    requires_sql=True,
                )
            return IntentClassification(
                query_type="simple_sql",
                confidence=0.80,
                rationale="Query asks for structured data.",
                metrics=metrics,
                dimensions=dimensions,
                filters=filters,
                requires_retrieval=False,
                requires_sql=True,
            )

        if has_hybrid:
            return IntentClassification(
                query_type="hybrid_sql_document",
                confidence=0.75,
                rationale="Query likely needs both document and SQL evidence.",
                metrics=metrics,
                dimensions=dimensions,
                filters=filters,
                requires_retrieval=True,
                requires_sql=True,
            )

        return IntentClassification(
            query_type="ambiguous",
            confidence=0.65,
            rationale="Could not confidently classify the query.",
            metrics=metrics,
            dimensions=dimensions,
            filters=filters,
            requires_clarification=True,
        )

    def _extract_metrics(self, q_lower: str) -> list[str]:
        found = []
        for pattern, metric in METRIC_PATTERNS:
            if re.search(pattern, q_lower):
                if metric not in found:
                    found.append(metric)
        return found

    def _extract_dimensions(self, q_lower: str) -> list[str]:
        found = []
        for pattern, dim in DIMENSION_PATTERNS:
            if re.search(pattern, q_lower):
                if dim not in found:
                    found.append(dim)
        return found

    def _extract_filters(self, q_lower: str) -> dict[str, str]:
        filters: dict[str, str] = {}
        for pattern, key, value in FILTER_PATTERNS:
            if re.search(pattern, q_lower):
                if key not in filters:
                    filters[key] = value
        return filters
