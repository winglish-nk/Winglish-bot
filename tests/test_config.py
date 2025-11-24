"""
設定管理のテスト
"""
import os

import pytest

# モジュールをインポートする前に環境変数を設定
os.environ["DISCORD_TOKEN"] = "test_token"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"


class TestValidateRequiredEnv:
    """validate_required_env関数のテスト"""

    def test_validate_required_env_success(self):
        """必要な環境変数がすべて設定されている場合"""
        from config import validate_required_env
        
        # 正常に実行されることを確認（例外が発生しない）
        try:
            validate_required_env()
        except SystemExit:
            pytest.fail("環境変数が設定されている場合はSystemExitが発生しないべき")

    def test_validate_required_env_missing_token(self, monkeypatch):
        """DISCORD_TOKENが設定されていない場合"""
        monkeypatch.delenv("DISCORD_TOKEN", raising=False)
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
        
        # モジュールをリロードするためにインポートを再実行
        import importlib
        import config
        importlib.reload(config)
        
        with pytest.raises(SystemExit):
            config.validate_required_env()

    def test_validate_required_env_missing_database(self, monkeypatch):
        """DATABASE_URLが設定されていない場合"""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token")
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("DATABASE_PUBLIC_URL", raising=False)
        
        # モジュールをリロード
        import importlib
        import config
        importlib.reload(config)
        
        with pytest.raises(SystemExit):
            config.validate_required_env()

