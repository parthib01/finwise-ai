from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth import SignupRequest, AuthResponse, LoginRequest
from app.deps.auth import get_current_user
from app.services.users import create_user, get_user_by_email
from app.services.sessions import create_session
from app.services.sessions import delete_session
from app.auth.security import create_access_token, verify_password


router = APIRouter()


@router.post("/signup", response_model=AuthResponse)
async def signup(payload: SignupRequest):

    # 1. Create user with hashed password
    user_id = await create_user(payload.email, payload.password)

    # 2. Create session (stateful part)
    session_id = await create_session(user_id)

    token = create_access_token(
    user_id=user_id,
    session_id=session_id  
)

    return AuthResponse(access_token=token)

@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    # 1. Find user
    user = await get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    # 2. Verify password
    if not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    user_id = str(user["id"])

    session_id =await create_session(user_id)

    token = create_access_token(
    user_id=user_id,
    session_id=session_id 
)

    return AuthResponse(access_token=token)

@router.post("/logout")
async def logout(
    identity: dict = Depends(get_current_user)
):
    session_id = identity["session_id"]

    await delete_session(session_id)

    return {
        "message": "Logged out successfully"
    }
