from app.services.messages import add_message, get_message_count


from app.tasks.summary_tasks import refresh_conversation_summary


async def store_message(
    state,
    background_tasks=None
):

    await add_message(
        conversation_id=state.conversation_id,
        role="assistant",
        content=state.response
    )

    total_messages = await get_message_count(
        state.conversation_id
    )

    print(
        f"\n📊 Total Messages: {total_messages}"
    )

    if (
        total_messages >= 10
        and
        total_messages % 10 == 0
    ):

        print(
            "\n📝 Summary Refresh Scheduled"
        )

        if background_tasks:

            background_tasks.add_task(
                refresh_conversation_summary,
                state.conversation_id
            )

    return state