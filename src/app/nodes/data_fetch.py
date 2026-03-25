from app.services.db_service import fetch_data_from_db

async def fetch_data(state):
    result = await fetch_data_from_db(
        intent=state.intent,
        user_id=state.user_id,
        parameters=state.parameters
    )

    state.db_result = result
    return state