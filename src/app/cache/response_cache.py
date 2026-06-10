from app.infra.redis_client import redis_client


CACHE_TTL = 3600


def build_cache_key(
    conversation_id: str,
    user_input: str
):
    return (
        f"response:{conversation_id}:{user_input.lower().strip()}"
    )


async def get_cached_response(
    conversation_id: str,
    user_input: str
):

    key = build_cache_key(
        conversation_id,
        user_input
    )

    response = await redis_client.get(
        key
    )

    if response:

        print(
            "⚡ Redis Response Cache HIT"
        )

        return response

    print(
        "💾 Redis Response Cache MISS"
    )

    return None


async def cache_response(
    conversation_id: str,
    user_input: str,
    response: str
):

    key = build_cache_key(
        conversation_id,
        user_input
    )

    await redis_client.set(
        key,
        response,
        ex=CACHE_TTL
    )

    print(
        "✅ Redis Response Cached"
    )