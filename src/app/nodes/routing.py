def route(state):
    if state.intent == "CALCULATE_EMI":
        return "CALCULATION_FLOW"

    if state.requires_db:
        return "DATA_FLOW"

    if state.intent == "POLICY_QUERY":
        return "POLICY_RAG_FLOW"
    
    return "EXPLANATION_FLOW"