def detect_mode(query: str) -> str:
    """
    Wrapper — actual implementation is in rag_service.py
    Kept here for backward compatibility with existing imports.
 
    Import directly from rag_service for the full implementation.
    """
    from app.services.policy_rag_service import detect_mode as _detect_mode
    return _detect_mode(query)


def extract_banks(query: str):
    banks = []

    if "sbi" in query.lower():
        banks.append("SBI")
    if "hdfc" in query.lower():
        banks.append("HDFC")
    if "icici" in query.lower():
        banks.append("ICICI")

    return banks