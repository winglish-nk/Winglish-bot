from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Optional

import asyncpg

from config import DATABASE_URL

logger = logging.getLogger('winglish.db')

_pool: Optional[asyncpg.Pool] = None


class DatabaseManager:
    """
    データベース接続プールを管理するクラス
    
    主な機能:
    - 接続プールの作成と管理
    - 接続のヘルスチェック
    - エラー時の自動リトライ（今後の拡張用）
    - 安全な接続取得（コンテキストマネージャー）
    """
    
    def __init__(self, database_url: str) -> None:
        """
        DatabaseManagerを初期化
        
        Args:
            database_url: PostgreSQL接続URL
        """
        self.database_url: str = database_url
        self._pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self, min_size: int = 1, max_size: int = 10, command_timeout: int = 60) -> None:
        """
        プールを初期化する
        
        Args:
            min_size: 最小接続数（デフォルト: 1）
            max_size: 最大接続数（デフォルト: 10）
            command_timeout: コマンドタイムアウト（秒、デフォルト: 60）
        
        Raises:
            asyncpg.PostgresConnectionError: データベース接続に失敗した場合
        """
        if self._pool is None:
            try:
                logger.info(f"データベース接続プールを初期化中... (min={min_size}, max={max_size})")
                self._pool = await asyncpg.create_pool(
                    self.database_url,
                    min_size=min_size,
                    max_size=max_size,
                    command_timeout=command_timeout,
                    server_settings={
                        'application_name': 'winglish-bot',
                        'timezone': 'UTC',
                    }
                )
                logger.info("✅ データベース接続プールの初期化が完了しました")
            except asyncpg.PostgresConnectionError as e:
                logger.error(f"❌ データベース接続エラー: {e}")
                raise
            except Exception as e:
                logger.error(f"❌ 予期しないデータベースエラー: {e}", exc_info=True)
                raise
    
    async def close(self) -> None:
        """
        プールを閉じる
        
        アプリケーション終了時に呼び出す
        """
        if self._pool:
            logger.info("データベース接続プールを閉じています...")
            await self._pool.close()
            self._pool = None
            logger.info("✅ データベース接続プールを閉じました")
    
    async def health_check(self) -> bool:
        """
        データベース接続のヘルスチェックを実行
        
        Returns:
            接続が正常な場合はTrue、それ以外はFalse
        """
        if self._pool is None:
            return False
        
        try:
            async with self._pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.warning(f"データベースヘルスチェック失敗: {e}")
            return False
    
    @asynccontextmanager
    async def acquire(self):
        """
        接続を取得（コンテキストマネージャー）
        
        Usage:
            async with db_manager.acquire() as conn:
                result = await conn.fetch("SELECT * FROM users")
        
        Yields:
            asyncpg.Connection: データベース接続
            
        Raises:
            RuntimeError: プールが初期化されていない場合
        """
        if self._pool is None:
            raise RuntimeError("Database pool not initialized. Call initialize() first.")
        
        async with self._pool.acquire() as conn:
            yield conn
    
    @property
    def pool(self) -> asyncpg.Pool:
        """
        プールを直接取得（後方互換性のため）
        
        Returns:
            データベース接続プール
            
        Raises:
            RuntimeError: プールが初期化されていない場合
        """
        if self._pool is None:
            raise RuntimeError("Database pool not initialized. Call initialize() first.")
        return self._pool


# グローバルなDatabaseManagerインスタンス（一元管理用）
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """
    グローバルなDatabaseManagerインスタンスを取得する
    
    Returns:
        DatabaseManagerインスタンス
        
    Raises:
        ValueError: DATABASE_URLが設定されていない場合
    """
    global _db_manager
    
    if DATABASE_URL is None:
        raise ValueError("DATABASE_URL is not set. Please configure it in environment variables.")
    
    if _db_manager is None:
        _db_manager = DatabaseManager(DATABASE_URL)
    
    return _db_manager


async def get_pool() -> asyncpg.Pool:
    """
    データベース接続プールを取得する（後方互換性のための関数）
    
    Note:
        新しいコードでは get_db_manager() の使用を推奨します。
    
    Returns:
        データベース接続プール
        
    Raises:
        ValueError: DATABASE_URLが設定されていない場合
        RuntimeError: プールが初期化されていない場合
    """
    global _pool
    
    # DatabaseManagerを使用して初期化
    db_manager = get_db_manager()
    
    # 既存のグローバルプールがあれば返す（後方互換性）
    if _pool is not None:
        return _pool
    
    # DatabaseManagerで初期化
    if db_manager._pool is None:
        await db_manager.initialize(min_size=1, max_size=10)
    
    _pool = db_manager.pool
    return _pool


async def init_db() -> None:
    """
    データベースを初期化し、スキーマを適用する
    
    Raises:
        FileNotFoundError: sql/schema.sql が見つからない場合
        asyncpg.PostgresError: データベースエラーが発生した場合
    """
    db_manager = get_db_manager()
    
    # DatabaseManagerで初期化（まだの場合）
    if db_manager._pool is None:
        await db_manager.initialize(min_size=1, max_size=10)
    
    try:
        with open("sql/schema.sql", "r", encoding="utf-8") as f:
            schema = f.read()
        async with db_manager.acquire() as con:
            await con.execute(schema)
        logger.info("✅ データベーススキーマの適用が完了しました")
    except FileNotFoundError:
        logger.error("❌ sql/schema.sql が見つかりません")
        raise
    except asyncpg.PostgresError as e:
        logger.error(f"❌ データベーススキーマ適用エラー: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ 予期しないエラー: {e}", exc_info=True)
        raise


async def close_db() -> None:
    """
    データベース接続プールを閉じる
    
    アプリケーション終了時に呼び出す
    """
    global _pool, _db_manager
    
    if _db_manager:
        await _db_manager.close()
        _db_manager = None
        _pool = None
    elif _pool:
        await _pool.close()
        _pool = None


# グローバルアクセス用（モジュールレベルで公開）
# 使用例: 
#   from db import get_db_manager
#   db_manager = get_db_manager()
#   async with db_manager.acquire() as conn: ...
__all__ = ['DatabaseManager', 'get_db_manager', 'get_pool', 'init_db', 'close_db']
