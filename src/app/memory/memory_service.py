from app.services.messages import get_messages

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


# 🔹 Type 2: Summary (stub for now)
async def get_summary(conversation_id: str):
    # Later: fetch from DB
    return "Previous conversation summary (stub)"