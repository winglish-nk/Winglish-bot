"""
エラーハンドリングユーティリティのテスト
"""
import asyncpg
import discord
import pytest
from unittest.mock import AsyncMock, MagicMock

from error_handler import ErrorHandler


class TestErrorHandler:
    """ErrorHandlerクラスのテスト"""

    @pytest.mark.asyncio
    async def test_safe_defer_success(self, mock_interaction):
        """deferが成功する場合のテスト"""
        result = await ErrorHandler.safe_defer(mock_interaction)
        
        assert result is True, "deferが成功した場合はTrueを返すべき"
        mock_interaction.response.defer.assert_called_once()

    @pytest.mark.asyncio
    async def test_safe_defer_already_responded(self, mock_interaction):
        """既に応答済みの場合のテスト"""
        mock_interaction.response.is_done.return_value = True
        result = await ErrorHandler.safe_defer(mock_interaction)
        
        assert result is False, "既に応答済みの場合はFalseを返すべき"

    @pytest.mark.asyncio
    async def test_handle_interaction_error_discord_http_403(self, mock_interaction):
        """Discord HTTP 403エラーの処理をテスト"""
        error = discord.HTTPException(
            response=MagicMock(status=403),
            message="Forbidden"
        )
        
        await ErrorHandler.handle_interaction_error(mock_interaction, error)
        
        # エラーメッセージが送信されることを確認
        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert "権限" in call_args[1]["content"] or "権限" in str(call_args)

    @pytest.mark.asyncio
    async def test_handle_interaction_error_database_error(self, mock_interaction):
        """データベース接続エラーの処理をテスト"""
        error = asyncpg.PostgresConnectionError("Connection failed")
        
        await ErrorHandler.handle_interaction_error(mock_interaction, error)
        
        # エラーメッセージが送信されることを確認
        mock_interaction.response.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_database_error_connection_error(self):
        """データベース接続エラーの処理をテスト"""
        error = asyncpg.PostgresConnectionError("Connection failed")
        message = await ErrorHandler.handle_database_error(error)
        
        assert "データベース" in message, "データベースエラーメッセージが含まれるべき"
        assert isinstance(message, str), "文字列を返すべき"

    @pytest.mark.asyncio
    async def test_handle_database_error_syntax_error(self):
        """SQL構文エラーの処理をテスト"""
        error = asyncpg.PostgresSyntaxError("Syntax error")
        message = await ErrorHandler.handle_database_error(error)
        
        assert "データベース" in message, "データベースエラーメッセージが含まれるべき"

    @pytest.mark.asyncio
    async def test_safe_edit_message_success(self, mock_interaction):
        """メッセージ編集が成功する場合のテスト"""
        embed = discord.Embed(title="Test")
        view = discord.ui.View()
        
        mock_interaction.response.is_done.return_value = False
        result = await ErrorHandler.safe_edit_message(
            mock_interaction,
            embed=embed,
            view=view
        )
        
        assert result is True, "編集が成功した場合はTrueを返すべき"
        mock_interaction.response.edit_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_safe_send_followup_success(self, mock_interaction):
        """followup送信が成功する場合のテスト"""
        result = await ErrorHandler.safe_send_followup(
            mock_interaction,
            content="Test message"
        )
        
        assert result is not None, "送信が成功した場合はメッセージオブジェクトを返すべき"
        mock_interaction.followup.send.assert_called_once()

