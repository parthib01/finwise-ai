from app.services.messages import get_messages
from app.infra.database import db
from app.infra.redis_client import redis_client


# ============================================================
# RECENT MESSAGES
# ============================================================

async def get_recent_messages(
    conversation_id: str,
    limit: int = 5
):

    messages = await get_messages(
        conversation_id
    )

    recent = messages[-limit:]

    return [
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in recent
    ]


# ============================================================
# SUMMARY RETRIEVAL
# ============================================================

async def get_summary(
    conversation_id: str
):

    cache_key = (
        f"summary:{conversation_id}"
    )

    cached = await redis_client.get(
        cache_key
    )

    if cached:

        print(
            "⚡ Redis Summary Cache HIT"
        )

        return cached

    print(
        "💾 Redis Summary Cache MISS"
    )

    query = """
        SELECT summary
        FROM conversation_summaries
        WHERE conversation_id = $1
    """

    rows = await db.fetch(
        query,
        conversation_id
    )

    if not rows:

        return (
            "No prior conversation context."
        )

    summary = rows[0]["summary"]

    await redis_client.set(
        cache_key,
        summary,
        ex=3600
    )

    return summary

# ============================================================
# SUMMARY SAVE
# ============================================================

async def save_summary(
    conversation_id: str,
    summary: str
):

    query = """
        INSERT INTO conversation_summaries
        (
            conversation_id,
            summary
        )
        VALUES ($1, $2)

        ON CONFLICT (conversation_id)

        DO UPDATE
        SET
            summary = $2,
            updated_at = NOW()
    """

    await db.execute(
        query,
        conversation_id,
        summary
    )

    await redis_client.set(
        f"summary:{conversation_id}",
        summary,
        ex=3600
    )

    print(
        "⚡ Redis Summary Cache Updated"
    )