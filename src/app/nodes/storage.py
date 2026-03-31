from app.services.messages import add_message
from app.memory.memory_service import get_summary, save_summary, get_recent_messages
from app.memory.summarizer import generate_summary


async def store_message(state):
    # Save assistant message
    await add_message(
        conversation_id=state.conversation_id,
        role="assistant",
        content=state.response
    )

    # 🔥 Update summary
    recent_messages = await get_recent_messages(state.conversation_id)

    old_summary = await get_summary(state.conversation_id)

    # new_summary = await generate_summary(old_summary, recent_messages)

    # await save_summary(state.conversation_id, new_summary)

    # TODO: move to background worker
    pass

    return state