from app.services.llm_service import generate_response_llm
from app.utils.logger import log_step


async def generate_response(state, memory):
    log_step("Generating Response", {
        "intent": state.intent,
        "db_result": state.db_result
    })
    
    # Build structured payload
    structured_data = {
        "intent": state.intent,
        "data": state.db_result
    }
    response = await generate_response_llm(
        user_input=state.user_input,
        structured_data=structured_data,
        memory=memory
    )

    state.response = response
    return state