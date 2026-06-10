from app.memory.memory_service import get_summary,save_summary, get_recent_messages

from app.memory.summarizer import generate_summary



async def refresh_conversation_summary(
    conversation_id: str
):
    print(
        "\n🧠 Background Summary Job Started"
    )

    recent_messages = await get_recent_messages(
        conversation_id,
        limit=20
    )

    old_summary = await get_summary(
        conversation_id
    )

    new_summary = await generate_summary(
        old_summary,
        recent_messages
    )

    await save_summary(
        conversation_id,
        new_summary
    )

    print(
        "✅ Background Summary Updated"
    )