from dotenv import load_dotenv
import os
import sys
from typing import Optional

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# DATABASE_URL  = os.getenv("DATABASE_URL")
# PUBLIC優先 → なければ従来のDATABASE_URLを見る
DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL")
DIFY_API_KEY  = os.getenv("DIFY_API_KEY")
DIFY_ENDPOINT_RUN  = os.getenv("DIFY_ENDPOINT_RUN", "https://api.dify.ai/v1/workflows/run").strip()
DIFY_ENDPOINT_CHAT = os.getenv("DIFY_ENDPOINT_CHAT", "https://api.dify.ai/v1/chat-messages").strip()
DIFY_API_KEY_QUESTION = os.getenv("DIFY_API_KEY_QUESTION")
DIFY_API_KEY_ANSWER = os.getenv("DIFY_API_KEY_ANSWER")
TEST_GUILD_ID = os.getenv("TEST_GUILD_ID")

# ロギング設定
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE")  # 例: "logs/winglish.log"


def validate_required_env() -> None:
    """
    起動時に必要な環境変数を検証する。
    不足している場合はエラーメッセージを表示して終了する。
    """
    missing: list[str] = []
    
    if not DISCORD_TOKEN or DISCORD_TOKEN == "YOUR_BOT_TOKEN":
        missing.append("DISCORD_TOKEN")
    
    if not DATABASE_URL:
        missing.append("DATABASE_PUBLIC_URL または DATABASE_URL")
    
    if missing:
        print("\n" + "="*60)
        print("❌ エラー: 必要な環境変数が設定されていません")
        print("="*60)
        for var in missing:
            print(f"  - {var}")
        print("\n以下のいずれかの方法で設定してください:")
        print("  1. .env ファイルに環境変数を追加")
        print("  2. Railway の Environment Variables に追加")
        print("  3. システム環境変数として設定")
        print("\n必要な環境変数の一覧:")
        print("  - DISCORD_TOKEN: Discord Bot のトークン")
        print("  - DATABASE_PUBLIC_URL または DATABASE_URL: PostgreSQL 接続URL")
        print("="*60 + "\n")
        sys.exit(1)


def get_optional_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """オプションの環境変数を取得する"""
    return os.getenv(key, default)
