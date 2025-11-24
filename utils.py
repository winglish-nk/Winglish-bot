from typing import Optional

import discord


def main_menu_view() -> discord.ui.View:
    """
    メインメニューのViewを作成する
    
    Returns:
        3つのボタン（英単語、英文解釈、長文読解）を含むView
    """
    v = discord.ui.View(timeout=None)
    v.add_item(discord.ui.Button(label="英単語", style=discord.ButtonStyle.primary, custom_id="menu:vocab"))
    v.add_item(discord.ui.Button(label="英文解釈", style=discord.ButtonStyle.primary, custom_id="menu:svocm"))
    v.add_item(discord.ui.Button(label="長文読解", style=discord.ButtonStyle.primary, custom_id="menu:reading"))
    return v


def info_embed(title: str, desc: str, color: Optional[int] = None) -> discord.Embed:
    """
    情報表示用のEmbedを作成する
    
    Args:
        title: Embedのタイトル
        desc: Embedの説明文
        color: Embedの色（デフォルト: 0x2b90d9）
    
    Returns:
        作成されたEmbed
    """
    embed_color = color if color is not None else 0x2b90d9
    e = discord.Embed(title=title, description=desc, color=embed_color)
    return e
