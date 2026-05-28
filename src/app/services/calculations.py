def calculate_emi(
    principal,
    annual_interest_rate,
    tenure_months
):

    monthly_rate = (
        annual_interest_rate
        / 12
        / 100
    )

    emi = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** tenure_months
        / (
            (1 + monthly_rate) ** tenure_months
            - 1
        )
    )

    emi = round(emi, 2)

    total_payment = round(
        emi * tenure_months,
        2
    )

    total_interest = round(
        total_payment - principal,
        2
    )

    return {

        "monthly_emi": emi,

        "total_payment": total_payment,

        "total_interest": total_interest,

        "interest_rate": annual_interest_rate,

        "tenure_months": tenure_months
    }