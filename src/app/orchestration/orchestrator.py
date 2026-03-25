from app.nodes.intent import classify_intent
from app.nodes.routing import route
from app.nodes.validation import validate_permission
from app.nodes.data_fetch import fetch_data
from app.nodes.response import generate_response
from app.nodes.output import validate_output
from app.nodes.storage import store_message
from app.nodes.calculation import calculate  

class Orchestrator:

    async def run(self, state, memory):
        # Step 1: Intent 
        state = classify_intent(state)

        # Step 2: Route 
        flow = route(state)

        # Step 3: Conditional paths
        if flow == "DATA_FLOW":
            state = validate_permission(state)
            state = await fetch_data(state)

        elif flow == "CALCULATION_FLOW":
            state = calculate(state)

        # Step 4: Generate response 
        state = await generate_response(state, memory)

        # Step 5: Validate output 
        state = validate_output(state)

        # Step 6: Store message 
        state = await store_message(state)

        return state.response