from app.services.llm_service import classify_intent_llm

async def classify_intent(state):

    intent = await classify_intent_llm(state.user_input)

    state.intent = intent

    # Set flags
    if intent == "CATEGORY_SPEND":
        state.requires_db = True

    elif intent == "CALCULATE_EMI":
        state.requires_db = False

        # TEMP: static params (we improve later)
        state.parameters = {
            "principal": 500000,
            "tenure_months": 24,
            "bank": "SBI",
            "loan_type": "home_loan"
        }

    else:
        state.requires_db = False

    return state
