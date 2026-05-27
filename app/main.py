from fastapi import FastAPI
from app.api.query_routes import router as query_router

app = FastAPI(
    title="Veridian AI",
    description="Evaluation-driven enterprise query engine",
    version="0.1.0",
)

app.include_router(query_router, prefix="/api")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Veridian AI",
        "version": "0.1.0",
    }
