from app.nodes.intent import classify_intent
from app.nodes.policy_rag import handle_policy_rag
from app.nodes.routing import route
from app.nodes.validation import validate_permission
from app.nodes.response import generate_response
from app.nodes.output import validate_output
from app.nodes.storage import store_message
from app.nodes.calculation import calculate

from app.utils.logger import (
    log_start,
    log_step,
    log_end
)

from app.cache.response_cache import (
    get_cached_response,
    cache_response
)


class Orchestrator:

    async def run(
        self,
        state,
        memory,
        background_tasks=None
    ):

        start_time = log_start(
            state.user_input
        )

        log_step(
            "Initial State",
            state.__dict__
        )

        # ====================================
        # RESPONSE CACHE CHECK
        # ====================================

        cached_response = await get_cached_response(
            state.conversation_id,
            state.user_input
        )

        if cached_response:

            print(
                "\n⚡ Returning Cached Response"
            )

            log_end(
                cached_response,
                start_time
            )

            return cached_response

        # ====================================
        # INTENT
        # ====================================

        state = await classify_intent(
            state
        )

        log_step(
            "Intent Classified",
            {
                "intent": state.intent,
                "params": state.parameters
            }
        )

        # ====================================
        # ROUTE
        # ====================================

        flow = route(state)

        log_step(
            "Route Selected",
            {
                "flow": flow
            }
        )

        # ====================================
        # EMI FLOW
        # ====================================

        if flow == "CALCULATION_FLOW":

            state = calculate(
                state
            )

            log_step(
                "Calculation Done",
                {
                    "result": state.db_result
                }
            )

        # ====================================
        # POLICY RAG FLOW
        # ====================================

        elif flow == "POLICY_RAG_FLOW":

            log_step(
                "Entering POLICY RAG FLOW",
                {}
            )

            state = await handle_policy_rag(
                state
            )

            log_step(
                "RAG Response Generated",
                {
                    "response": state.response
                }
            )

        # ====================================
        # NORMAL RESPONSE GENERATION
        # ====================================

        if flow != "POLICY_RAG_FLOW":

            state = await generate_response(
                state,
                memory
            )

            log_step(
                "Response Generated",
                {
                    "response": state.response
                }
            )

        # ====================================
        # CACHE RESPONSE
        # ====================================

        await cache_response(
            state.conversation_id,
            state.user_input,
            state.response
        )

        # ====================================
        # STORE MESSAGE
        # ====================================

        state = await store_message(
            state,
            background_tasks
        )

        log_step(
            "Message Stored"
        )

        log_end(
            state.response,
            start_time
        )

        return state.response