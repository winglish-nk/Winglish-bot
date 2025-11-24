"""
pytest設定と共通フィクスチャ
"""
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# テスト用の環境変数を設定
os.environ.setdefault("DISCORD_TOKEN", "test_token_for_testing")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("DATABASE_PUBLIC_URL", "postgresql://test:test@localhost/test")


@pytest.fixture
def mock_interaction():
    """Discord Interactionのモック"""
    interaction = MagicMock()
    interaction.user.id = 123456789
    interaction.user.mention = "<@123456789>"
    interaction.guild_id = 987654321
    interaction.channel_id = 111222333
    interaction.channel = MagicMock()
    interaction.response.is_done.return_value = False
    interaction.response.defer = AsyncMock()
    interaction.response.edit_message = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.edit_original_response = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.message = MagicMock()
    interaction.message.edit = AsyncMock()
    interaction.message.components = []
    return interaction


@pytest.fixture
def mock_database_pool():
    """データベース接続プールのモック"""
    pool = AsyncMock()
    connection = AsyncMock()
    pool.acquire = AsyncMock()
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=connection)
    pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
    connection.fetch = AsyncMock()
    connection.fetchrow = AsyncMock()
    connection.execute = AsyncMock()
    connection.fetchval = AsyncMock(return_value=1)
    return pool, connection

