from fastapi import APIRouter, Depends, HTTPException
from app.deps.auth import get_current_user
from app.services.messages import add_user_message, get_messages
from app.infra.database import db
from app.schemas.messages import MessageCreate, MessageList

router = APIRouter()

@router.post("/conversations/{conversation_id}/messages")
async def post_message(
    conversation_id: str,
    payload: MessageCreate,
    identity: dict = Depends(get_current_user),
):
    user_id = identity["user_id"]
    # Ownership check
    ownership_query = """
        SELECT 1 FROM conversations
        WHERE id = $1 AND user_id = $2
    """
    rows = await db.fetch(ownership_query, conversation_id, user_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await add_user_message(conversation_id, payload.content)
    return {"status": "message added"}


@router.get("/conversations/{conversation_id}/messages", response_model=MessageList)
async def list_messages(
    conversation_id: str,
    identity: dict = Depends(get_current_user),
):
    user_id = identity["user_id"]
    ownership_query = """
        SELECT 1 FROM conversations
        WHERE id = $1 AND user_id = $2
    """
    rows = await db.fetch(ownership_query, conversation_id, user_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await get_messages(conversation_id)
    return {"messages": messages}
