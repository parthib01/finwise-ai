from datetime import datetime, timedelta, timezone
from app.infra.database import db
import uuid


async def create_session(user_id: str):
    session_id = str(uuid.uuid4())

    query = """
        INSERT INTO sessions (id, user_id, expires_at)
        VALUES ($1, $2, $3)
    """

    expires = datetime.now(timezone.utc) + timedelta(days=7)

    await db.execute(query, session_id, user_id, expires)

    return session_id

async def delete_session(session_id: str):
    query = """
        DELETE FROM sessions
        WHERE id = $1
    """
    await db.execute(query, session_id)
