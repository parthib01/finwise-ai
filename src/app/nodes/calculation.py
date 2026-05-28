from app.services.calculations import calculate_emi



def calculate(state):

    if state.intent != "CALCULATE_EMI":
        return state

    params = state.parameters

    principal = params.get(
        "principal"
    )

    interest_rate = params.get(
        "interest_rate"
    )

    tenure_months = params.get(
        "tenure_months"
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    if (
        principal is None
        or interest_rate is None
        or tenure_months is None
    ):

        state.db_result = (
            "Missing EMI parameters"
        )

        return state

    # ========================================================
    # EMI CALCULATION
    # ========================================================

    result = calculate_emi(

        principal=principal,

        annual_interest_rate=interest_rate,

        tenure_months=tenure_months
    )

    state.db_result = result

    return state