import re

from app.schemas.sql import CompiledSQLQuery, SQLExecutionError
from app.semantic_layer.schema_registry import WAREHOUSE_SCHEMA


FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "COPY",
    "ATTACH",
    "DETACH",
    "INSTALL",
    "LOAD",
    "EXPORT",
    "IMPORT",
    "PRAGMA",
    "CALL",
    "VACUUM",
]

FORBIDDEN_FUNCTIONS = ["read_csv", "read_csv_auto", "parquet_scan", "read_parquet", "glob"]


class SQLSafetyValidator:
    def validate(self, compiled: CompiledSQLQuery) -> SQLExecutionError | None:
        sql = compiled.sql
        normalized = re.sub(r"\s+", " ", sql.strip()).upper()
        if not normalized.startswith("SELECT "):
            return SQLExecutionError(code="UNSAFE_SQL", message="Only SELECT statements are allowed.")
        if ";" in sql:
            return SQLExecutionError(code="UNSAFE_SQL", message="Multiple statements or semicolons are not allowed.")
        if "--" in sql or "/*" in sql or "*/" in sql:
            return SQLExecutionError(code="UNSAFE_SQL", message="SQL comments are not allowed.")
        for keyword in FORBIDDEN_KEYWORDS:
            if re.search(rf"\b{keyword}\b", normalized):
                return SQLExecutionError(code="UNSAFE_SQL", message=f"Forbidden SQL keyword: {keyword}.")
        for fn in FORBIDDEN_FUNCTIONS:
            if re.search(rf"\b{fn.upper()}\s*\(", normalized):
                return SQLExecutionError(code="UNSAFE_SQL", message=f"Forbidden SQL function: {fn}.")
        table_names = re.findall(r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, flags=re.IGNORECASE)
        for table in table_names:
            if not WAREHOUSE_SCHEMA.has_table(table):
                return SQLExecutionError(code="UNSAFE_SQL", message=f"Unknown table '{table}'.")
        parameter_error = self._validate_parameters(compiled.parameters)
        if parameter_error:
            return parameter_error
        return None

    def _validate_parameters(self, parameters: list[object]) -> SQLExecutionError | None:
        for value in parameters:
            if not isinstance(value, (str, int, float)):
                return SQLExecutionError(code="UNSAFE_PARAMETER", message="SQL parameters must be scalar values.")
            if not isinstance(value, str):
                continue
            normalized = value.upper()
            if ";" in value or "--" in value or "/*" in value or "*/" in value:
                return SQLExecutionError(code="UNSAFE_PARAMETER", message="SQL parameter contains forbidden SQL control text.")
            for keyword in FORBIDDEN_KEYWORDS:
                if re.search(rf"\b{keyword}\b", normalized):
                    return SQLExecutionError(code="UNSAFE_PARAMETER", message="SQL parameter contains forbidden SQL keyword text.")
        return None
