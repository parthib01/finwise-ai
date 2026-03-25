from app.services.messages import add_message

async def store_message(state):
    await add_message(
        conversation_id=state.conversation_id,
        role="assistant",
        content=state.response
    )
    return state