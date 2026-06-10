from uuid import uuid4
from app.infra.database import db

async def add_message(conversation_id: str, role: str, content: str):
    query = """
        INSERT INTO messages (id, conversation_id, role, content)
        VALUES ($1, $2, $3, $4)
    """
    message_id = str(uuid4())

    await db.execute(query, message_id, conversation_id, role, content)

    return message_id

async def add_user_message(conversation_id: str, content: str):
    return await add_message(conversation_id, "user", content)


async def get_messages(conversation_id: str):
    query = """
        SELECT id, role, content, created_at
        FROM messages
        WHERE conversation_id = $1
        ORDER BY created_at ASC
    """
    rows = await db.fetch(query, conversation_id)
    return [
        {
            "id": row["id"],
            "role": row["role"],
            "content": row["content"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]

async def get_message_count(
    conversation_id: str
):
    query = """
        SELECT COUNT(*) AS count
        FROM messages
        WHERE conversation_id = $1
    """

    row = await db.fetch(
        query,
        conversation_id
    )

    return row[0]["count"]
