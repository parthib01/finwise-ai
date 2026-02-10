from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

# ========================
# Password Hashing
# ========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # bcrypt limit protection
    safe_pass = password[:72]
    return pwd_context.hash(safe_pass)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    safe_pass = plain_password[:72]
    return pwd_context.verify(safe_pass, hashed_password)


# ========================
# JWT Handling
# ========================
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 45

def create_access_token(user_id: str, session_id: str, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload = {
        "sub": user_id,
        "sid": session_id,
        "exp": expire,
        "iat": now,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload         
    except JWTError:
        return None