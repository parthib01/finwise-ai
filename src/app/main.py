# src/app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.health import router as health_router
from app.infra.database import db

DATABASE_URL = "postgresql://postgres:Parthib@01@localhost:5432/finwise_ai"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await db.connect(DATABASE_URL)
    yield
    # shutdown      
    await db.disconnect()



def create_app() -> FastAPI:
    app = FastAPI(
        title="FinWise AI",
        version="0.1.0",
    )

    app.include_router(health_router, prefix="/health")

    return app

app = create_app()
