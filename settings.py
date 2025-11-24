"""
設定管理クラス

環境変数からの設定値を管理し、型安全なアクセスを提供します。
"""
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()


@dataclass
class DiscordConfig:
    """Discord関連の設定"""
    token: str
    test_guild_id: Optional[int] = None
    
    @classmethod
    def from_env(cls) -> "DiscordConfig":
        """環境変数からDiscord設定を読み込む"""
        token = os.getenv("DISCORD_TOKEN") or ""
        test_guild_id_str = os.getenv("TEST_GUILD_ID")
        test_guild_id = int(test_guild_id_str) if test_guild_id_str else None
        
        return cls(
            token=token,
            test_guild_id=test_guild_id
        )


@dataclass
class DatabaseConfig:
    """データベース関連の設定"""
    url: str
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """環境変数からデータベース設定を読み込む"""
        url = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL") or ""
        return cls(url=url)


@dataclass
class DifyConfig:
    """Dify API関連の設定"""
    api_key_question: Optional[str] = None
    api_key_answer: Optional[str] = None
    endpoint_run: str = "https://api.dify.ai/v1/workflows/run"
    endpoint_chat: str = "https://api.dify.ai/v1/chat-messages"
    
    @classmethod
    def from_env(cls) -> "DifyConfig":
        """環境変数からDify設定を読み込む"""
        endpoint_run = os.getenv("DIFY_ENDPOINT_RUN", "https://api.dify.ai/v1/workflows/run").strip()
        endpoint_chat = os.getenv("DIFY_ENDPOINT_CHAT", "https://api.dify.ai/v1/chat-messages").strip()
        
        return cls(
            api_key_question=os.getenv("DIFY_API_KEY_QUESTION"),
            api_key_answer=os.getenv("DIFY_API_KEY_ANSWER"),
            endpoint_run=endpoint_run,
            endpoint_chat=endpoint_chat
        )


@dataclass
class LoggingConfig:
    """ロギング関連の設定"""
    level: str = "INFO"
    file: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "LoggingConfig":
        """環境変数からロギング設定を読み込む"""
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file=os.getenv("LOG_FILE")
        )


@dataclass
class Settings:
    """アプリケーション全体の設定"""
    discord: DiscordConfig
    database: DatabaseConfig
    dify: DifyConfig
    logging: LoggingConfig
    
    @classmethod
    def from_env(cls) -> "Settings":
        """環境変数から全設定を読み込む"""
        return cls(
            discord=DiscordConfig.from_env(),
            database=DatabaseConfig.from_env(),
            dify=DifyConfig.from_env(),
            logging=LoggingConfig.from_env()
        )
    
    def validate(self) -> list[str]:
        """
        必須設定が揃っているか検証する
        
        Returns:
            不足している設定項目のリスト（空の場合はすべて揃っている）
        """
        missing: list[str] = []
        
        if not self.discord.token or self.discord.token == "YOUR_BOT_TOKEN":
            missing.append("DISCORD_TOKEN")
        
        if not self.database.url:
            missing.append("DATABASE_PUBLIC_URL または DATABASE_URL")
        
        return missing


# グローバル設定インスタンス
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    設定インスタンスを取得する（シングルトンパターン）
    
    Returns:
        Settingsインスタンス
    """
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


def reload_settings() -> Settings:
    """
    設定を再読み込みする
    
    Returns:
        新しいSettingsインスタンス
    """
    global _settings
    _settings = Settings.from_env()
    return _settings

