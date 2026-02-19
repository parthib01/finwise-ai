from fastapi import APIRouter, Depends
from app.deps.auth import get_current_user

router = APIRouter()

@router.get("/me")
async def me(identity: dict = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user_id": identity["user_id"],
        "session_id": identity["session_id"]
    }
