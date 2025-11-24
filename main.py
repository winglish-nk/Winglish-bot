# main.py
import sys
from typing import Any

try:
    import discord
    from discord.ext import commands
except ImportError:
    print("❌ discord.py がインストールされていません。`pip install -r requirements.txt` を実行してください。")
    sys.exit(1)

from config import DISCORD_TOKEN, TEST_GUILD_ID, LOG_LEVEL, LOG_FILE, validate_required_env
from db import init_db, close_db, get_db_manager
from cogs.menu import MenuView
from logger_config import setup_logging, get_logger

# --- ログ設定 ---
setup_logging(log_level=LOG_LEVEL, log_file=LOG_FILE)
logger = get_logger('winglish')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class WinglishBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        try:
            # DatabaseManagerの初期化
            db_manager = get_db_manager()
            await db_manager.initialize()
            await init_db()  # スキーマ適用
            logger.info("✅ データベース初期化完了")
        except Exception as e:
            logger.critical(f"❌ データベース初期化に失敗しました: {e}", exc_info=True)
            raise

        cogs = ["cogs.onboarding", "cogs.menu", "cogs.vocab", "cogs.notebook", "cogs.svocm", "cogs.reading", "cogs.admin"]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Cog 読み込み完了: {cog}")
            except Exception as e:
                logger.error(f"❌ Cog 読み込み失敗: {cog} - {e}")

        self.add_view(MenuView())
        logger.info("✅ 永続 View 登録完了")
        
        #--- スラッシュコマンド同期 ---
        try:
            if TEST_GUILD_ID:
                guild = discord.Object(id=int(TEST_GUILD_ID))
                synced_commands = await self.tree.sync(guild=guild)
                logger.info(f"✅ スラッシュコマンド同期完了（テストギルド: {TEST_GUILD_ID}）")
                logger.info(f"📊 同期されたコマンド数: {len(synced_commands)}")
                for cmd in sorted(synced_commands, key=lambda x: x.name):
                    logger.info(f"  ✅ /{cmd.name}")
            else:
                synced_commands = await self.tree.sync()
                logger.info("✅ スラッシュコマンド同期完了（グローバル）")
                logger.info(f"📊 同期されたコマンド数: {len(synced_commands)}")
                for cmd in sorted(synced_commands, key=lambda x: x.name):
                    logger.info(f"  ✅ /{cmd.name}")
        except ValueError as e:
            logger.error(f"❌ TEST_GUILD_ID が無効です: {e}")
        except discord.HTTPException as e:
            logger.error(f"❌ スラッシュコマンド同期失敗 (HTTP {e.status}): {e.text}")
        except Exception as e:
            logger.error(f"❌ スラッシュコマンド同期失敗: {e}", exc_info=True)

    async def on_ready(self) -> None:
        logger.info(f"✅ Logged in as {self.user} ({self.user.id})")

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        logger.exception(f"⚠️ イベントエラー ({event_method})")

# --- スラッシュコマンド ---
bot = WinglishBot()

@bot.tree.command(name="start", description="Winglishを開始（個人鍵チャンネルにメニューを出します）")
async def start_cmd(interaction: discord.Interaction):
    """個人チャンネルを取得または作成し、メニューを送信"""
    await interaction.response.defer(ephemeral=True)
    
    try:
        from cogs.menu import MenuView
        from utils import info_embed
        
        # Onboarding Cogのインスタンスを取得
        onboarding_cog = bot.get_cog('Onboarding')
        if onboarding_cog is None:
            logger.error("Onboarding Cogが見つかりません")
            await interaction.followup.send(
                "❌ エラーが発生しました。Botを再起動してください。",
                ephemeral=True
            )
            return
        
        # 個人チャンネルを取得または作成
        member = interaction.user
        if not isinstance(member, discord.Member):
            logger.warning(f"memberがdiscord.Memberではありません: {type(member)}")
            await interaction.followup.send(
                "❌ エラーが発生しました。サーバー内で実行してください。",
                ephemeral=True
            )
            return
        
        logger.info(f"個人チャンネルを取得または作成: user={member.name} ({member.id})")
        channel = await onboarding_cog.ensure_private_channel(member)
        logger.info(f"個人チャンネル取得成功: {channel.name} ({channel.id})")
        
        # メニューを送信（既存チャンネルでも常に送信）
        try:
            await channel.send(
                embed=info_embed("Winglish - 学習メニュー", "学習メニューを選んでください。"),
                view=MenuView()
            )
            logger.info(f"メニューを送信しました: {channel.name}")
        except Exception as send_error:
            logger.error(f"メニュー送信エラー: {send_error}", exc_info=True)
            await interaction.followup.send(
                f"❌ メニューの送信に失敗しました: {send_error}",
                ephemeral=True
            )
            return
        
        await interaction.followup.send(
            f"✅ あなたの個人チャンネル <#{channel.id}> にメニューを送りました！",
            ephemeral=True
        )
    except Exception as e:
        logger.error(f"start_cmd エラー: {e}", exc_info=True)
        error_msg = f"❌ エラーが発生しました: {str(e)}"
        if len(error_msg) > 200:
            error_msg = "❌ エラーが発生しました。管理者に連絡してください。"
        await interaction.followup.send(
            error_msg,
            ephemeral=True
        )

# --- 実行 ---
if __name__ == "__main__":
    # 環境変数の検証
    try:
        validate_required_env()
    except SystemExit:
        sys.exit(1)
    except Exception as e:
        logger.critical(f"❌ 環境変数検証中にエラーが発生しました: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("="*60)
    logger.info("🚀 Winglish Bot を起動しています...")
    logger.info("="*60)
    
    try:
        bot.run(DISCORD_TOKEN, log_handler=None)  # discord.pyのログは無効化（自前のログを使用）
    except discord.LoginFailure:
        logger.critical("❌ Discordトークンが無効です。")
        logger.critical("   DISCORD_TOKEN の値を確認してください。")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 ユーザーによって中断されました。")
    except discord.PrivilegedIntentsRequired as e:
        logger.critical(f"❌ 必要な権限（Intents）が有効化されていません: {e}")
        logger.critical("   Discord Developer Portal で Intents を有効化してください。")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"💥 予期しないエラー: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("="*60)
        logger.info("👋 Winglish Bot を終了します")
        logger.info("データベース接続を閉じています...")
        try:
            import asyncio
            asyncio.run(close_db())
        except Exception as e:
            logger.warning(f"データベース接続のクローズ時にエラーが発生しました: {e}")
        logger.info("="*60)