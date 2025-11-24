"""
ユーティリティ関数のテスト
"""
import discord

from utils import info_embed, main_menu_view


class TestInfoEmbed:
    """info_embed関数のテスト"""

    def test_info_embed_creation(self):
        """Embedの基本的な作成をテスト"""
        embed = info_embed("テストタイトル", "テスト説明")
        
        assert isinstance(embed, discord.Embed), "Embed型であるべき"
        assert embed.title == "テストタイトル", "タイトルが正しく設定されるべき"
        assert embed.description == "テスト説明", "説明が正しく設定されるべき"
        assert embed.color == 0x2b90d9, "デフォルトの色が設定されるべき"

    def test_info_embed_custom_color(self):
        """カスタムカラーのEmbed作成をテスト"""
        custom_color = 0xFF0000
        embed = info_embed("テスト", "説明", color=custom_color)
        
        assert embed.color == custom_color, "カスタム色が設定されるべき"

    def test_info_embed_empty_strings(self):
        """空文字列でも正常に動作するかテスト"""
        embed = info_embed("", "")
        
        assert isinstance(embed, discord.Embed), "空文字列でもEmbedが作成されるべき"


class TestMainMenuView:
    """main_menu_view関数のテスト"""

    def test_main_menu_view_creation(self):
        """メインメニューViewの作成をテスト"""
        view = main_menu_view()
        
        assert isinstance(view, discord.ui.View), "View型であるべき"
        assert view.timeout is None, "timeoutはNoneであるべき（永続View）"

    def test_main_menu_view_buttons(self):
        """メインメニューのボタンが正しく追加されているかテスト"""
        view = main_menu_view()
        
        # 3つのボタンがあることを確認
        buttons = [item for item in view.children if isinstance(item, discord.ui.Button)]
        assert len(buttons) == 3, "3つのボタンがあるべき"
        
        # ボタンのラベルを確認
        labels = [btn.label for btn in buttons]
        assert "英単語" in labels, "「英単語」ボタンがあるべき"
        assert "英文解釈" in labels, "「英文解釈」ボタンがあるべき"
        assert "長文読解" in labels, "「長文読解」ボタンがあるべき"

    def test_main_menu_view_button_ids(self):
        """ボタンのcustom_idが正しく設定されているかテスト"""
        view = main_menu_view()
        buttons = [item for item in view.children if isinstance(item, discord.ui.Button)]
        
        custom_ids = [btn.custom_id for btn in buttons]
        assert "menu:vocab" in custom_ids, "vocabボタンのIDがあるべき"
        assert "menu:svocm" in custom_ids, "svocmボタンのIDがあるべき"
        assert "menu:reading" in custom_ids, "readingボタンのIDがあるべき"

