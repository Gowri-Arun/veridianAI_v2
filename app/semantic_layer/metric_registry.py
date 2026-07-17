from pydantic import BaseModel, Field


class MetricDefinition(BaseModel):
    canonical_name: str
    display_name: str
    synonyms: list[str]
    source_table: str
    value_column: str
    default_aggregation: str
    allowed_aggregations: list[str]
    valid_dimensions: list[str]
    unit: str
    description: str
    forbidden_confusions: list[str] = Field(default_factory=list)


METRICS: dict[str, MetricDefinition] = {
    "revenue": MetricDefinition(
        canonical_name="revenue",
        display_name="Recognized revenue",
        synonyms=["revenue", "recognized revenue", "income"],
        source_table="revenue",
        value_column="recognized_revenue",
        default_aggregation="sum",
        allowed_aggregations=["sum", "avg"],
        valid_dimensions=["quarter", "region", "segment", "product"],
        unit="currency",
        description="Revenue already recognized in the warehouse.",
        forbidden_confusions=["bookings", "pipeline"],
    ),
    "bookings": MetricDefinition(
        canonical_name="bookings",
        display_name="Bookings",
        synonyms=["bookings", "booked revenue"],
        source_table="revenue",
        value_column="bookings",
        default_aggregation="sum",
        allowed_aggregations=["sum", "avg"],
        valid_dimensions=["quarter", "region", "segment", "product"],
        unit="currency",
        description="Booked sales value, distinct from recognized revenue.",
        forbidden_confusions=["revenue", "pipeline"],
    ),
    "marketing_spend": MetricDefinition(
        canonical_name="marketing_spend",
        display_name="Marketing spend",
        synonyms=["marketing spend", "ad spend", "ads", "marketing"],
        source_table="marketing_spend",
        value_column="spend",
        default_aggregation="sum",
        allowed_aggregations=["sum", "avg"],
        valid_dimensions=["quarter", "region", "channel"],
        unit="currency",
        description="Marketing investment by channel and region.",
        forbidden_confusions=["customer_acquisition_cost", "cac"],
    ),
    "churn": MetricDefinition(
        canonical_name="churn",
        display_name="Churn rate",
        synonyms=["churn", "churn rate", "customer loss", "lost customers", "attrition"],
        source_table="churn",
        value_column="churn_rate",
        default_aggregation="avg",
        allowed_aggregations=["avg"],
        valid_dimensions=["quarter", "region", "segment"],
        unit="rate",
        description="Customer churn rate by quarter, region, and segment.",
        forbidden_confusions=["support_tickets"],
    ),
    "customer_count": MetricDefinition(
        canonical_name="customer_count",
        display_name="Customer count",
        synonyms=["customers", "customer count", "number of customers"],
        source_table="customers",
        value_column="customer_id",
        default_aggregation="count",
        allowed_aggregations=["count"],
        valid_dimensions=["region", "segment", "industry", "signup_quarter", "status"],
        unit="count",
        description="Count of customer records.",
        forbidden_confusions=["subscriptions", "accounts"],
    ),
    "support_tickets": MetricDefinition(
        canonical_name="support_tickets",
        display_name="Support tickets",
        synonyms=["support tickets", "support issues", "escalations", "tickets"],
        source_table="support_tickets",
        value_column="ticket_id",
        default_aggregation="count",
        allowed_aggregations=["count"],
        valid_dimensions=["quarter", "region", "segment", "product", "issue_type", "severity", "escalated"],
        unit="count",
        description="Count of support ticket records.",
        forbidden_confusions=["churn"],
    ),
    "pipeline": MetricDefinition(
        canonical_name="pipeline",
        display_name="Pipeline value",
        synonyms=["pipeline", "sales pipeline", "pipeline value"],
        source_table="sales_pipeline",
        value_column="pipeline_value",
        default_aggregation="sum",
        allowed_aggregations=["sum", "avg"],
        valid_dimensions=["quarter", "region", "segment"],
        unit="currency",
        description="Potential future sales pipeline value.",
        forbidden_confusions=["revenue", "bookings"],
    ),
    "conversion_rate": MetricDefinition(
        canonical_name="conversion_rate",
        display_name="Conversion rate",
        synonyms=["conversion rate", "conversion"],
        source_table="sales_pipeline",
        value_column="conversion_rate",
        default_aggregation="avg",
        allowed_aggregations=["avg"],
        valid_dimensions=["quarter", "region", "segment"],
        unit="rate",
        description="Average pipeline conversion rate.",
        forbidden_confusions=[],
    ),
    "product_usage": MetricDefinition(
        canonical_name="product_usage",
        display_name="Usage score",
        synonyms=["product usage", "usage", "usage score"],
        source_table="product_usage",
        value_column="usage_score",
        default_aggregation="avg",
        allowed_aggregations=["avg"],
        valid_dimensions=["quarter", "region", "segment", "product"],
        unit="score",
        description="Average product usage score.",
        forbidden_confusions=[],
    ),
    "subscriptions": MetricDefinition(
        canonical_name="subscriptions",
        display_name="Subscriptions",
        synonyms=["subscriptions", "subscription count", "number of subscriptions"],
        source_table="subscriptions",
        value_column="subscription_id",
        default_aggregation="count",
        allowed_aggregations=["count"],
        valid_dimensions=["product", "plan_type", "start_quarter", "renewal_quarter", "status"],
        unit="count",
        description="Count of subscription records.",
        forbidden_confusions=["customers", "accounts"],
    ),
    "region_target": MetricDefinition(
        canonical_name="region_target",
        display_name="Revenue target",
        synonyms=["revenue target", "target", "region target"],
        source_table="region_targets",
        value_column="revenue_target",
        default_aggregation="sum",
        allowed_aggregations=["sum", "avg"],
        valid_dimensions=["quarter", "region"],
        unit="currency",
        description="Regional revenue target.",
        forbidden_confusions=["pipeline_target"],
    ),
}


def get_metric(name: str) -> MetricDefinition | None:
    return METRICS.get(name)


def all_metrics() -> list[MetricDefinition]:
    return list(METRICS.values())


def metric_synonym_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}
    for metric in METRICS.values():
        for synonym in metric.synonyms:
            if synonym in lookup and lookup[synonym] != metric.canonical_name:
                raise ValueError(f"Duplicate metric synonym: {synonym}")
            lookup[synonym] = metric.canonical_name
    return lookup


def resolve_metric_term(term: str) -> MetricDefinition | None:
    canonical = metric_synonym_lookup().get(term.lower().strip())
    return METRICS.get(canonical) if canonical else None
