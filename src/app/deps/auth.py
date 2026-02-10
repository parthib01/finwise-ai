from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.security import decode_access_token
from app.infra.database import db

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    # ---- STEP 1: JWT Verification ----
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")
    session_id = payload.get("sid")

    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Malformed token: no session"
        )

    # ---- STEP 2: SESSION CHECK (CORRECT) ----
    query = """
        SELECT id FROM sessions
        WHERE id = $1
        AND user_id = $2
        AND expires_at > NOW()
    """

    rows = await db.fetch(query, session_id, user_id)

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please login again."
        )

    return {
        "user_id": user_id,
        "session_id": session_id
    }