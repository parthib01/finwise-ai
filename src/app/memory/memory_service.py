from app.services.messages import get_messages
from app.infra.database import db

# 🔹 Type 1: Recent messages
async def get_recent_messages(conversation_id: str, limit: int = 5):
    messages = await get_messages(conversation_id)

    # take last N
    recent = messages[-limit:]

    return [
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in recent
    ]


# 🔹 Type 2: Summary
async def get_summary(conversation_id: str):
    query = """
        SELECT summary FROM conversation_summaries
        WHERE conversation_id = $1
    """
    rows = await db.fetch(query, conversation_id)

    if not rows:
        return "No prior conversation context."

    return rows[0]["summary"]

# 🔹 Save / Update summary
async def save_summary(conversation_id: str, summary: str):
    query = """
        INSERT INTO conversation_summaries (conversation_id, summary)
        VALUES ($1, $2)
        ON CONFLICT (conversation_id)
        DO UPDATE SET summary = $2, updated_at = NOW()
    """
    await db.execute(query, conversation_id, summary)