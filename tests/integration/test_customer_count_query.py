import asyncio

from app.api.query_routes import query
from app.schemas.query import QueryRequest


def test_customer_count_query_executes_with_segment_and_region_filters():
    response = asyncio.run(query(QueryRequest(query="How many enterprise customers are in APAC?")))

    assert response.status == "completed"
    assert response.sql_results[0]["rows"] == [{"customer_count": 14}]
