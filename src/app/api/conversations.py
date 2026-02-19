from fastapi import APIRouter, Depends
from app.deps.auth import get_current_user
from app.services.conversations import create_conversation

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/")
async def start_conversation(
    identity: dict = Depends(get_current_user)
):
    return await create_conversation(identity["user_id"])
