# main.py
import logging
import sys
from typing import Any
import os
from datetime import datetime

try:
    import discord
    from discord.ext import commands
except ImportError:
    print("❌ discord.py がインストールされていません。`pip install -r requirements.txt` を実行してください。")
    sys.exit(1)

from config import DISCORD_TOKEN, TEST_GUILD_ID, validate_required_env
from db import init_db
from utils import info_embed
from cogs.menu import MenuView

# --- ログ設定 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('winglish')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class WinglishBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        await init_db()
        logger.info("✅ データベース初期化完了")

        cogs = ["cogs.onboarding", "cogs.menu", "cogs.vocab", "cogs.svocm", "cogs.reading", "cogs.admin"]
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
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                logger.info(f"✅ スラッシュコマンド同期完了（テストギルド: {TEST_GUILD_ID}）")
            else:
                await self.tree.sync()
                logger.info("✅ スラッシュコマンド同期完了（グローバル）")
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
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("あなたの個人チャンネルにメニューを送ります。", ephemeral=True)

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
        logger.info("="*60)