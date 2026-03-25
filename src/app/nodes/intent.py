def classify_intent(state):
    text = state.user_input.lower()

    if "emi" in text:
        state.intent = "CALCULATE_EMI"
        state.requires_db = False
        state.parameters = {
            "principal": 500000,
            "tenure_months": 24,
            "bank": "SBI",
            "loan_type": "home_loan"
        }
        return state

    if "spending" in text:
        state.intent = "CATEGORY_SPEND"
        state.requires_db = True
        state.parameters = {}
        return state

    state.intent = "EXPLANATION"
    state.requires_db = False
    return state