from pydantic import BaseModel, Field


class TableSchema(BaseModel):
    name: str
    columns: dict[str, str]
    row_count: int


class SchemaRegistry(BaseModel):
    tables: dict[str, TableSchema]
    joins_allowed: bool = False
    supported_joins: list[dict[str, str]] = Field(default_factory=list)

    def has_table(self, table: str) -> bool:
        return table in self.tables

    def has_column(self, table: str, column: str) -> bool:
        return table in self.tables and column in self.tables[table].columns


WAREHOUSE_SCHEMA = SchemaRegistry(
    joins_allowed=False,
    tables={
        "revenue": TableSchema(
            name="revenue",
            row_count=144,
            columns={
                "quarter": "VARCHAR",
                "region": "VARCHAR",
                "segment": "VARCHAR",
                "product": "VARCHAR",
                "recognized_revenue": "DOUBLE",
                "bookings": "DOUBLE",
                "pipeline_value": "DOUBLE",
                "gross_margin": "DOUBLE",
            },
        ),
        "customers": TableSchema(
            name="customers",
            row_count=400,
            columns={
                "customer_id": "VARCHAR",
                "customer_name": "VARCHAR",
                "region": "VARCHAR",
                "segment": "VARCHAR",
                "industry": "VARCHAR",
                "signup_quarter": "VARCHAR",
                "status": "VARCHAR",
            },
        ),
        "marketing_spend": TableSchema(
            name="marketing_spend",
            row_count=48,
            columns={
                "quarter": "VARCHAR",
                "region": "VARCHAR",
                "channel": "VARCHAR",
                "spend": "DOUBLE",
                "campaign_name": "VARCHAR",
                "leads_generated": "INTEGER",
            },
        ),
        "churn": TableSchema(
            name="churn",
            row_count=48,
            columns={
                "quarter": "VARCHAR",
                "region": "VARCHAR",
                "segment": "VARCHAR",
                "churn_rate": "DOUBLE",
                "churned_customers": "INTEGER",
                "starting_customers": "INTEGER",
                "retention_rate": "DOUBLE",
            },
        ),
        "support_tickets": TableSchema(
            name="support_tickets",
            row_count=447,
            columns={
                "ticket_id": "VARCHAR",
                "customer_id": "VARCHAR",
                "quarter": "VARCHAR",
                "region": "VARCHAR",
                "segment": "VARCHAR",
                "product": "VARCHAR",
                "issue_type": "VARCHAR",
                "severity": "VARCHAR",
                "escalated": "BOOLEAN",
                "response_time_hours": "DOUBLE",
                "resolution_time_hours": "DOUBLE",
            },
        ),
        "product_usage": TableSchema(
            name="product_usage",
            row_count=144,
            columns={
                "quarter": "VARCHAR",
                "region": "VARCHAR",
                "segment": "VARCHAR",
                "product": "VARCHAR",
                "active_users": "INTEGER",
                "usage_score": "DOUBLE",
                "feature_adoption_rate": "DOUBLE",
                "avg_sessions_per_account": "DOUBLE",
            },
        ),
        "sales_pipeline": TableSchema(
            name="sales_pipeline",
            row_count=48,
            columns={
                "quarter": "VARCHAR",
                "region": "VARCHAR",
                "segment": "VARCHAR",
                "pipeline_value": "DOUBLE",
                "opportunities_created": "INTEGER",
                "win_rate": "DOUBLE",
                "conversion_rate": "DOUBLE",
                "avg_sales_cycle_days": "INTEGER",
            },
        ),
        "subscriptions": TableSchema(
            name="subscriptions",
            row_count=496,
            columns={
                "subscription_id": "VARCHAR",
                "customer_id": "VARCHAR",
                "product": "VARCHAR",
                "plan_type": "VARCHAR",
                "start_quarter": "VARCHAR",
                "renewal_quarter": "VARCHAR",
                "arr": "DOUBLE",
                "status": "VARCHAR",
            },
        ),
        "region_targets": TableSchema(
            name="region_targets",
            row_count=16,
            columns={
                "quarter": "VARCHAR",
                "region": "VARCHAR",
                "revenue_target": "DOUBLE",
                "pipeline_target": "DOUBLE",
                "churn_target": "DOUBLE",
                "gross_margin_target": "DOUBLE",
            },
        ),
    },
)
