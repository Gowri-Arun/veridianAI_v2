from app.schemas.sql import CompiledSQLQuery, SQLQuerySpec
from app.semantic_layer.dimension_registry import get_dimension
from app.semantic_layer.schema_registry import WAREHOUSE_SCHEMA


AGGREGATIONS = {
    "sum": "SUM",
    "avg": "AVG",
    "count": "COUNT",
}


class SQLCompiler:
    def compile(self, spec: SQLQuerySpec) -> CompiledSQLQuery:
        self._validate_identifier(spec.source_table, spec.value_column)
        agg = AGGREGATIONS[spec.aggregation]
        metric_alias = spec.metric
        select_parts = []
        group_columns = []
        for dimension_name in spec.dimensions:
            dimension = get_dimension(dimension_name)
            if not dimension:
                raise ValueError(f"Unknown dimension: {dimension_name}")
            self._validate_identifier(spec.source_table, dimension.column_name)
            select_parts.append(dimension.column_name)
            group_columns.append(dimension.column_name)
        if spec.aggregation == "count":
            select_parts.append(f"{agg}({spec.value_column}) AS {metric_alias}")
        else:
            select_parts.append(f"{agg}({spec.value_column}) AS {metric_alias}")

        sql = f"SELECT {', '.join(select_parts)} FROM {spec.source_table}"
        parameters: list = []
        where_clauses = []
        for condition in spec.filters:
            self._validate_identifier(spec.source_table, condition.column)
            where_clauses.append(f"{condition.column} = ?")
            parameters.append(condition.value)
        if spec.periods:
            self._validate_identifier(spec.source_table, "quarter")
            placeholders = ", ".join(["?"] * len(spec.periods))
            where_clauses.append(f"quarter IN ({placeholders})")
            parameters.extend(spec.periods)
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        if group_columns:
            sql += " GROUP BY " + ", ".join(group_columns)
        if spec.periods and not group_columns and spec.query_shape in {"period_comparison", "absolute_change", "percentage_change"}:
            sql = sql.replace(f"{agg}({spec.value_column}) AS {metric_alias}", f"quarter, {agg}({spec.value_column}) AS {metric_alias}")
            sql += " GROUP BY quarter"
        if spec.order_by:
            direction = spec.order_direction.upper()
            if direction not in {"ASC", "DESC"}:
                raise ValueError("Unsupported sort direction.")
            sql += f" ORDER BY {metric_alias} {direction}"
        elif "GROUP BY quarter" in sql:
            sql += " ORDER BY quarter"
        if spec.limit:
            sql += f" LIMIT {min(spec.limit, 100)}"
        return CompiledSQLQuery(
            query_id=spec.query_id,
            sql=sql,
            parameters=parameters,
            explanation=f"Deterministically compiled {spec.query_shape} for {spec.metric} from {spec.source_table}.",
        )

    def _validate_identifier(self, table: str, column: str) -> None:
        if not WAREHOUSE_SCHEMA.has_table(table):
            raise ValueError(f"Unknown table: {table}")
        if not WAREHOUSE_SCHEMA.has_column(table, column):
            raise ValueError(f"Unknown column '{column}' for table '{table}'")
