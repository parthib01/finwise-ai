from app.services.policy_rag_service import query_policy_rag


async def handle_policy_rag(state):

    response = await query_policy_rag(state.user_input)

    state.response = response
    return state