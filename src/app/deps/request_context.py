# src/app/deps/request_context.py

from typing import Dict

async def get_request_context() -> Dict[str, str]:
    """
    Placeholder for per-request context.
    Will later include:
    - user_id
    - session_id
    - request_id
    """
    return {}
