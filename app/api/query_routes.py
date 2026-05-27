from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    query: str
    status: str
    message: str


@router.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest):
    return QueryResponse(
        query=request.query,
        status="not_implemented",
        message="Query pipeline will be implemented in later weeks.",
    )
