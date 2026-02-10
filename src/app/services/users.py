from app.infra.database import db
from app.auth.security import hash_password
import uuid


async def create_user(email: str, password: str):
    hashed = hash_password(password)

    query = """
        INSERT INTO users (id, email, hashed_password)
        VALUES ($1, $2, $3)
        RETURNING id
    """

    user_id = str(uuid.uuid4())

    await db.execute(query, user_id, email, hashed)

    return user_id

async def get_user_by_email(email: str):
    query = """
        SELECT id, email, hashed_password
        FROM users
        WHERE email = $1
    """
    rows = await db.fetch(query, email)
    return rows[0] if rows else None