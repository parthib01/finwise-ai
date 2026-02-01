import asyncpg
from typing import Optional

class Database:
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self, dsn : str):
        self._pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=2,
            max_size=10,
        )

    async def disconnect(self):
        if self._pool:
            await self._pool.close()

    async def fetch(self, query:str, *args):
        async with self._pool.acquire() as connection:
            return await connection.fetch(query, *args)
        
    async def execute(self, query:str, *args):
        async with self._pool.acquire() as connection:
            return await connection.execute(query, *args)
        
db = Database()
