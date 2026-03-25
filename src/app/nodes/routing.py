def route(state):
    if state.intent == "CALCULATE_EMI":
        return "CALCULATION_FLOW"

    if state.requires_db:
        return "DATA_FLOW"

    return "EXPLANATION_FLOW"