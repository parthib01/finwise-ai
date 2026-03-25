from app.services.llm_service import generate_response_llm

async def generate_response(state, memory):
    response = await generate_response_llm(
        user_input=state.user_input,
        intent=state.intent,
        db_result=state.db_result,
        memory=memory
    )

    state.response = response
    return state