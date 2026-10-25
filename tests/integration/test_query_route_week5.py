from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def post(query: str):
    response = client.post("/api/query", json={"query": query, "include_trace": True})
    assert response.status_code == 200
    return response.json()


def test_sql_lookup_route():
    data = post("What was enterprise revenue in APAC in Q4 2025?")
    assert data["status"] == "completed"
    assert data["sql_results"]
    assert data["sql_results"][0]["row_count"] == 1


def test_period_comparison_route():
    data = post("Compare APAC enterprise revenue in Q3 and Q4 2025.")
    rows = data["sql_results"][0]["rows"]
    assert {row["quarter"] for row in rows} == {"Q3_2025", "Q4_2025"}


def test_absolute_change_route():
    data = post("How much did APAC enterprise revenue decline from Q3 to Q4 2025?")
    assert data["comparison_results"]
    assert data["comparison_results"][0]["direction"] == "decrease"


def test_hybrid_route_returns_sql_and_docs_without_synthesis():
    data = post("Why did enterprise revenue decline in APAC despite higher marketing spend?")
    assert data["sql_results"]
    assert data["retrieved_documents"]
    assert data["synthesis_status"] == "not_implemented"


def test_delete_blocked():
    data = post("Delete all revenue records.")
    assert data["status"] == "rejected"
    assert not data["sql_results"]


def test_ambiguous_sales_clarification():
    data = post("How were sales?")
    assert data["status"] == "needs_clarification"
    assert not data["sql_results"]


def test_unknown_metric_no_sql():
    data = post("What was lunar velocity in Atlantis?")
    assert data["status"] in {"error", "needs_clarification"}
    assert not data["sql_results"]


def test_retrieval_only_route_still_works():
    data = post("Find the APAC pricing memo.")
    assert data["retrieved_documents"]
    assert not data["sql_results"]
