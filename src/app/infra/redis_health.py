from app.infra.redis_client import redis_client

async def check_redis():

    try:

        await redis_client.ping()

        print(
            "✅ Redis Connected"
        )

    except Exception as e:

        print(
            f"❌ Redis Error: {e}"
        )