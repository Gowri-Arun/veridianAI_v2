from pydantic import ConfigDict
from pydantic import BaseModel


class DimensionDefinition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    canonical_name: str
    display_name: str
    synonyms: list[str]
    column_name: str
    allowed_values: list[str]
    compatible_metrics: list[str]
    description: str

DIMENSIONS: dict[str, DimensionDefinition] = {
    "quarter": DimensionDefinition(
        canonical_name="quarter",
        display_name="Quarter",
        synonyms=["quarter", "period", "q1", "q2", "q3", "q4"],
        column_name="quarter",
        allowed_values=["Q1_2025", "Q2_2025", "Q3_2025", "Q4_2025"],
        compatible_metrics=["revenue", "bookings", "marketing_spend", "churn", "support_tickets", "pipeline", "conversion_rate", "product_usage", "region_target"],
        description="Dataset quarter in Qn_YYYY format.",
    ),
    "region": DimensionDefinition(
        canonical_name="region",
        display_name="Region",
        synonyms=["region", "geography", "geo", "apac", "emea", "latam", "north america"],
        column_name="region",
        allowed_values=["APAC", "EMEA", "LATAM", "North America"],
        compatible_metrics=["revenue", "bookings", "marketing_spend", "churn", "customer_count", "support_tickets", "pipeline", "conversion_rate", "product_usage", "region_target"],
        description="Sales/customer region.",
    ),
    "segment": DimensionDefinition(
        canonical_name="segment",
        display_name="Segment",
        synonyms=["segment", "customer segment", "enterprise", "smb", "mid-market"],
        column_name="segment",
        allowed_values=["Enterprise", "Mid-Market", "SMB"],
        compatible_metrics=["revenue", "bookings", "churn", "customer_count", "support_tickets", "pipeline", "conversion_rate", "product_usage"],
        description="Customer segment.",
    ),
    "product": DimensionDefinition(
        canonical_name="product",
        display_name="Product",
        synonyms=["product", "flowops", "insightos", "metrichub"],
        column_name="product",
        allowed_values=["FlowOps", "InsightOS", "MetricHub"],
        compatible_metrics=["revenue", "bookings", "support_tickets", "product_usage", "subscriptions"],
        description="Product name.",
    ),
    "channel": DimensionDefinition(
        canonical_name="channel",
        display_name="Marketing channel",
        synonyms=["channel", "marketing channel", "events", "paid search", "content"],
        column_name="channel",
        allowed_values=["Content", "Events", "Paid Search"],
        compatible_metrics=["marketing_spend"],
        description="Marketing channel.",
    ),
    "industry": DimensionDefinition(
        canonical_name="industry",
        display_name="Industry",
        synonyms=["industry"],
        column_name="industry",
        allowed_values=["Finance", "Healthcare", "Retail", "Tech"],
        compatible_metrics=["customer_count"],
        description="Customer industry.",
    ),
    "status": DimensionDefinition(
        canonical_name="status",
        display_name="Status",
        synonyms=["status", "active", "churned"],
        column_name="status",
        allowed_values=["Active", "Churned"],
        compatible_metrics=["customer_count", "subscriptions"],
        description="Customer or subscription status.",
    ),
    "severity": DimensionDefinition(
        canonical_name="severity",
        display_name="Ticket severity",
        synonyms=["severity", "low", "medium", "high"],
        column_name="severity",
        allowed_values=["High", "Low", "Medium"],
        compatible_metrics=["support_tickets"],
        description="Support ticket severity.",
    ),
}


REGION_ALIASES = {
    "apac": "APAC",
    "asia pacific": "APAC",
    "asia-pacific": "APAC",
    "emea": "EMEA",
    "europe": "EMEA",
    "latam": "LATAM",
    "north america": "North America",
    "na": "North America",
}

SEGMENT_ALIASES = {
    "enterprise": "Enterprise",
    "enterprise customers": "Enterprise",
    "enterprise clients": "Enterprise",
    "large customers": "Enterprise",
    "smb": "SMB",
    "small business": "SMB",
    "small businesses": "SMB",
    "mid-market": "Mid-Market",
    "midmarket": "Mid-Market",
    "mid market": "Mid-Market",
}

PRODUCT_ALIASES = {
    "flowops": "FlowOps",
    "insightos": "InsightOS",
    "metric hub": "MetricHub",
    "metrichub": "MetricHub",
}

CHANNEL_ALIASES = {
    "events": "Events",
    "paid search": "Paid Search",
    "content": "Content",
}

STATUS_ALIASES = {
    "active": "Active",
    "churned": "Churned",
}

SEVERITY_ALIASES = {
    "high": "High",
    "low": "Low",
    "medium": "Medium",
}


def get_dimension(name: str) -> DimensionDefinition | None:
    return DIMENSIONS.get(name)


def all_dimensions() -> list[DimensionDefinition]:
    return list(DIMENSIONS.values())


def dimension_synonym_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}
    for dimension in DIMENSIONS.values():
        for synonym in dimension.synonyms:
            lookup[synonym] = dimension.canonical_name
    return lookup


def normalize_categorical_value(dimension: str, value: str) -> str | None:
    value_lower = value.lower().strip()
    alias_maps: dict[str, dict[str, str]] = {
        "region": REGION_ALIASES,
        "segment": SEGMENT_ALIASES,
        "product": PRODUCT_ALIASES,
        "channel": CHANNEL_ALIASES,
        "status": STATUS_ALIASES,
        "severity": SEVERITY_ALIASES,
    }
    if dimension in alias_maps:
        return alias_maps[dimension].get(value_lower)
    dim = get_dimension(dimension)
    if not dim:
        return None
    for allowed in dim.allowed_values:
        if allowed.lower() == value_lower:
            return allowed
    return None
