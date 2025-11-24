from typing import Optional

import asyncpg

from config import DATABASE_URL

_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """
    データベース接続プールを取得する（シングルトンパターン）
    
    Returns:
        データベース接続プール
    """
    global _pool
    if _pool is None:
        if DATABASE_URL is None:
            raise ValueError("DATABASE_URL is not set. Please configure it in environment variables.")
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def init_db() -> None:
    """
    データベースを初期化し、スキーマを適用する
    
    Raises:
        FileNotFoundError: sql/schema.sql が見つからない場合
        asyncpg.PostgresError: データベースエラーが発生した場合
    """
    pool = await get_pool()
    with open("sql/schema.sql", "r", encoding="utf-8") as f:
        schema = f.read()
    async with pool.acquire() as con:
        await con.execute(schema)
