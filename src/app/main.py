# src/app/main.py

from fastapi import FastAPI
from app.api.health import router as health_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="FinWise AI",
        version="0.1.0",
    )

    app.include_router(health_router, prefix="/health")

    return app

app = create_app()
