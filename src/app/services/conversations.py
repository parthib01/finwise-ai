import uuid
from datetime import datetime, timezone
from app.infra.database import db


async def create_conversation(user_id: str):
    conversation_id = str(uuid.uuid4())

    query = """
        INSERT INTO conversations (id, user_id, created_at, last_active_at)
        VALUES ($1, $2, NOW(), NOW())
    """

    await db.execute(query, conversation_id, user_id)

    return {
        "conversation_id": conversation_id,
        "created_at": datetime.now(timezone.utc)
    }
