def calculate_emi(principal, rate, tenure_months):
    monthly_rate = rate / (12 * 100)

    emi = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** tenure_months
        / ((1 + monthly_rate) ** tenure_months - 1)
    )

    return round(emi, 2)