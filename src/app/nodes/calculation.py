from app.services.calculations import calculate_emi
from app.services.bank_data import BANK_RATES

def calculate(state):
    if state.intent == "CALCULATE_EMI":
        params = state.parameters

        principal = params.get("principal")
        tenure = params.get("tenure_months")
        bank = params.get("bank")
        loan_type = params.get("loan_type")

        # Fetch rate
        rate = BANK_RATES.get(bank, {}).get(loan_type)

        if rate is None:
            state.db_result = "Bank or loan type not supported"
            return state

        emi = calculate_emi(principal, rate, tenure)

        state.db_result = emi

    return state