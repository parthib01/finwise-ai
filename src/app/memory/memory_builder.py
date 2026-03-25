from app.memory.memory_service import get_recent_messages, get_summary

async def build_memory(conversation_id: str):
    recent_messages = await get_recent_messages(conversation_id)
    summary = await get_summary(conversation_id)

    return {
        "recent_messages": recent_messages,
        "summary": summary
    }