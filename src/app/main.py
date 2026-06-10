# src/app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager

import app
from app.api.health import router as health_router
from app.infra.database import db
from app.api.auth import router as auth_router
from app.api.users import router as user_router
from app.api.conversations import router as conversations_router
from app.api.messages import router as messages_router
from app.infra.redis_health import check_redis


DATABASE_URL = "postgresql://postgres:Parthib%4001@localhost:5432/finwise_ai"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await db.connect(DATABASE_URL)
    await check_redis()
    yield
    # shutdown      
    await db.disconnect()



def create_app() -> FastAPI:
    app = FastAPI(
        title="FinWise AI",
        version="0.1.0",
        lifespan=lifespan
    )

    app.include_router(health_router, prefix="/health")
    app.include_router(auth_router, prefix="/auth")
    app.include_router(user_router, prefix="/users")
    app.include_router(conversations_router, prefix="/conversations")
    app.include_router(messages_router)

    return app

app = create_app()
