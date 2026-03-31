from app.nodes.intent import classify_intent
from app.nodes.routing import route
from app.nodes.validation import validate_permission
from app.nodes.data_fetch import fetch_data
from app.nodes.response import generate_response
from app.nodes.output import validate_output
from app.nodes.storage import store_message
from app.nodes.calculation import calculate  
from app.utils.logger import log_start, log_step, log_end


class Orchestrator:

    async def run(self, state, memory):

        start_time = log_start(state.user_input)

        log_step("Initial State", state.__dict__)

        # 1. Intent
        state = await classify_intent(state)
        log_step("Intent Classified", {"intent": state.intent, "params": state.parameters})

        # 2. Route
        flow = route(state)
        log_step("Route Selected", {"flow": flow})

        # 3. Data Fetch (if needed)
        if flow == "DATA_FLOW":
            state = await fetch_data(state)
            log_step("Data Fetched", {"db_result": state.db_result})

        # 4. Calculation
        if flow == "CALCULATION_FLOW":
            state = calculate(state)
            log_step("Calculation Done", {"result": state.db_result})

        # 5. Response
        state = await generate_response(state, memory)
        log_step("Response Generated", {"response": state.response})

        # 6. Store
        state = await store_message(state)
        # log_step("Message Stored + Summary Updated")
        log_step("Message Stored")

        log_end(state.response, start_time)

        return state.response
        