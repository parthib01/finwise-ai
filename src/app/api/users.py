from fastapi import APIRouter, Depends
from app.deps.auth import get_current_user

router = APIRouter()

@router.get("/me")
async def me(user_id: str = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user_id": user_id
    }
