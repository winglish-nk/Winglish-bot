"""
エラーハンドリングユーティリティ
各Cogで統一されたエラー処理を提供する
"""
import logging
from typing import Optional, Callable, Awaitable

import discord
import asyncpg

logger = logging.getLogger('winglish.error_handler')


class ErrorHandler:
    """エラーハンドリングを統一管理するクラス"""
    
    @staticmethod
    async def handle_interaction_error(
        interaction: discord.Interaction,
        error: Exception,
        user_message: Optional[str] = None,
        log_context: Optional[str] = None
    ) -> None:
        """
        Interactionでのエラーを処理する
        
        Args:
            interaction: Discord Interaction
            error: 発生した例外
            user_message: ユーザーに表示するメッセージ（Noneの場合はデフォルトメッセージ）
            log_context: ログに記録するコンテキスト情報
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        # ログに記録
        context_info = f" [{log_context}]" if log_context else ""
        logger.error(
            f"Interactionエラー{context_info}: {error_type}: {error_msg}",
            exc_info=True,
            extra={
                "user_id": interaction.user.id if interaction.user else None,
                "guild_id": interaction.guild_id,
                "channel_id": interaction.channel_id if interaction.channel else None,
            }
        )
        
        # ユーザー向けメッセージを決定
        if user_message is None:
            if isinstance(error, discord.HTTPException):
                if error.status == 403:
                    user_message = "❌ 権限が不足しています。Botに必要な権限があるか確認してください。"
                elif error.status == 429:
                    user_message = "⚠️ レート制限に達しました。少し待ってから再試行してください。"
                elif error.status >= 500:
                    user_message = "❌ Discordサーバーでエラーが発生しました。しばらく待ってから再試行してください。"
                else:
                    user_message = f"❌ エラーが発生しました（HTTP {error.status}）。"
            elif isinstance(error, asyncpg.PostgresConnectionError):
                user_message = "❌ データベース接続エラーが発生しました。管理者に連絡してください。"
            elif isinstance(error, asyncpg.PostgresSyntaxError):
                user_message = "❌ データベースエラーが発生しました。管理者に連絡してください。"
            elif isinstance(error, asyncpg.PostgresError):
                user_message = "❌ データベースエラーが発生しました。管理者に連絡してください。"
            else:
                user_message = "❌ 予期しないエラーが発生しました。管理者に連絡してください。"
        
        # ユーザーにエラーメッセージを送信
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    user_message,
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    user_message,
                    ephemeral=True
                )
        except Exception as send_error:
            logger.error(f"エラーメッセージ送信に失敗: {send_error}")
    
    @staticmethod
    async def safe_defer(interaction: discord.Interaction) -> bool:
        """
        安全にdeferを実行する
        
        Returns:
            deferが成功したかどうか
        """
        try:
            if not interaction.response.is_done():
                await interaction.response.defer(thinking=False)
                return True
        except discord.InteractionResponded:
            # 既に応答済み
            return False
        except discord.HTTPException as e:
            logger.warning(f"defer失敗 (HTTP {e.status}): {e.text}")
            return False
        except Exception as e:
            logger.warning(f"defer失敗: {e}")
            return False
        return False
    
    @staticmethod
    async def safe_edit_message(
        interaction: discord.Interaction,
        embed: Optional[discord.Embed] = None,
        view: Optional[discord.ui.View] = None,
        content: Optional[str] = None
    ) -> bool:
        """
        安全にメッセージを編集する
        
        Returns:
            編集が成功したかどうか
        """
        try:
            if not interaction.response.is_done():
                await interaction.response.edit_message(
                    embed=embed,
                    view=view,
                    content=content
                )
                return True
        except discord.InteractionResponded:
            pass
        except discord.HTTPException as e:
            logger.warning(f"メッセージ編集失敗 (HTTP {e.status}): {e.text}")
            return False
        
        try:
            await interaction.edit_original_response(
                embed=embed,
                view=view,
                content=content
            )
            return True
        except discord.HTTPException as e:
            logger.warning(f"メッセージ編集失敗 (HTTP {e.status}): {e.text}")
            return False
        except Exception as e:
            logger.warning(f"メッセージ編集失敗: {e}")
        
        # 最後の手段: 元のメッセージを直接編集
        try:
            if interaction.message:
                await interaction.message.edit(
                    embed=embed,
                    view=view,
                    content=content
                )
                return True
        except Exception as e:
            logger.warning(f"メッセージ直接編集も失敗: {e}")
        
        return False
    
    @staticmethod
    async def safe_send_followup(
        interaction: discord.Interaction,
        content: Optional[str] = None,
        embed: Optional[discord.Embed] = None,
        view: Optional[discord.ui.View] = None,
        ephemeral: bool = False
    ) -> Optional[discord.WebhookMessage]:
        """
        安全にfollowupを送信する
        
        Returns:
            送信されたメッセージ（失敗時はNone）
        """
        try:
            return await interaction.followup.send(
                content=content,
                embed=embed,
                view=view,
                ephemeral=ephemeral
            )
        except discord.HTTPException as e:
            logger.error(f"followup送信失敗 (HTTP {e.status}): {e.text}")
            return None
        except Exception as e:
            logger.error(f"followup送信失敗: {e}")
            return None
    
    @staticmethod
    async def handle_database_error(
        error: Exception,
        context: str = ""
    ) -> str:
        """
        データベースエラーを処理し、ログに記録する
        
        Returns:
            ユーザー向けエラーメッセージ
        """
        error_type = type(error).__name__
        error_msg = str(error)
        
        context_info = f" [{context}]" if context else ""
        logger.error(
            f"データベースエラー{context_info}: {error_type}: {error_msg}",
            exc_info=True
        )
        
        if isinstance(error, asyncpg.PostgresConnectionError):
            return "❌ データベースに接続できませんでした。管理者に連絡してください。"
        elif isinstance(error, asyncpg.PostgresSyntaxError):
            return "❌ データベースエラーが発生しました。管理者に連絡してください。"
        elif isinstance(error, asyncpg.PostgresError):
            return "❌ データベースエラーが発生しました。管理者に連絡してください。"
        else:
            return "❌ 予期しないエラーが発生しました。管理者に連絡してください。"


def with_error_handler(
    user_message: Optional[str] = None,
    log_context: Optional[str] = None
):
    """
    デコレータ: 関数をエラーハンドラーでラップする
    
    Usage:
        @with_error_handler(user_message="カスタムエラーメッセージ")
        async def my_handler(interaction: discord.Interaction):
            ...
    """
    def decorator(func: Callable[..., Awaitable[None]]):
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            try:
                return await func(interaction, *args, **kwargs)
            except Exception as e:
                await ErrorHandler.handle_interaction_error(
                    interaction,
                    e,
                    user_message=user_message,
                    log_context=log_context or func.__name__
                )
        return wrapper
    return decorator

