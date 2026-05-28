from app.services.llm_service import classify_intent_llm


from app.services.emi_parser_service import extract_emi_parameters



# ============================================================
# 🔹 INTENT CLASSIFICATION NODE
# ============================================================

async def classify_intent(state):

    # ========================================================
    # CLASSIFY INTENT
    # ========================================================

    intent = await classify_intent_llm(
        state.user_input
    )

    state.intent = intent

    print(
        f"\n🧠 Classified Intent: {intent}"
    )

    # ========================================================
    # CALCULATE EMI FLOW
    # ========================================================

    if intent == "CALCULATE_EMI":

        state.requires_db = False

        print(
            "\n⚡ Extracting EMI parameters..."
        )

        params = await extract_emi_parameters(
            state.user_input
        )

        state.parameters = params

        print(
            f"✅ EMI Params: {params}"
        )

    # ========================================================
    # POLICY QUERY FLOW
    # ========================================================

    elif intent == "POLICY_QUERY":

        state.requires_db = False

    # ========================================================
    # EXPLANATION FLOW
    # ========================================================

    else:

        state.requires_db = False

    return state