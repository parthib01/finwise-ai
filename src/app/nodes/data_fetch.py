from app.services.db_service import fetch_data_from_db
from app.utils.logger import log_step

async def fetch_data(state):
    result = await fetch_data_from_db(
        intent=state.intent,
        user_id=state.user_id,
        parameters=state.parameters
    )

    log_step("DB RAW RESULT", result)

    state.db_result = result
    return state