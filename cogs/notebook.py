from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

import discord
from discord.ext import commands

from db import get_db_manager
from error_handler import ErrorHandler
from cogs.vocab import VocabSessionView, ensure_defer, safe_edit

logger = logging.getLogger('winglish.notebook')


class Notebook(commands.Cog):
    """単語帳機能のCog"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.app_commands.command(
        name="notebook_create",
        description="新しい単語帳を作成"
    )
    async def notebook_create(
        self,
        interaction: discord.Interaction,
        name: str,
        description: str = ""
    ) -> None:
        """単語帳を作成"""
        user_id = str(interaction.user.id)
        
        try:
            db_manager = get_db_manager()
            async with db_manager.acquire() as conn:
                # 同名の単語帳があるかチェック
                existing = await conn.fetchrow("""
                    SELECT notebook_id FROM vocabulary_notebooks 
                    WHERE user_id = $1 AND name = $2
                """, user_id, name)
                
                if existing:
                    await interaction.response.send_message(
                        f"❌ 既に「{name}」という名前の単語帳が存在します。",
                        ephemeral=True
                    )
                    return
                
                # 単語帳を作成
                notebook_id = await conn.fetchval("""
                    INSERT INTO vocabulary_notebooks (user_id, name, description)
                    VALUES ($1, $2, $3)
                    RETURNING notebook_id
                """, user_id, name, description)
            
            await interaction.response.send_message(
                f"✅ 単語帳「{name}」を作成しました！\n"
                f"説明: {description if description else 'なし'}",
                ephemeral=True
            )
            logger.info(f"ユーザー {user_id} が単語帳「{name}」を作成しました")
        except Exception as e:
            await ErrorHandler.handle_interaction_error(
                interaction,
                e,
                log_context="notebook.notebook_create"
            )

    @discord.app_commands.command(
        name="notebook_list",
        description="自分の単語帳一覧を表示"
    )
    async def notebook_list(self, interaction: discord.Interaction) -> None:
        """単語帳一覧を表示（ユーザー個人の単語帳のみ）"""
        user_id = str(interaction.user.id)
        
        try:
            db_manager = get_db_manager()
            async with db_manager.acquire() as conn:
                notebooks = await conn.fetch("""
                    SELECT 
                        n.notebook_id,
                        n.name,
                        n.description,
                        n.is_auto,
                        COUNT(nw.word_id) as word_count
                    FROM vocabulary_notebooks n
                    LEFT JOIN notebook_words nw ON n.notebook_id = nw.notebook_id
                    WHERE n.user_id = $1 AND n.is_system = FALSE
                    GROUP BY n.notebook_id, n.name, n.description, n.is_auto
                    ORDER BY n.created_at DESC
                """, user_id)
            
            if not notebooks:
                await interaction.response.send_message(
                    "📚 単語帳がまだありません。`/notebook_create` で作成しましょう！\n"
                    "または `/notebook_list_system` でシステム推奨単語帳を確認できます。",
                    ephemeral=True
                )
                return
            
            # Embedで表示
            embed = discord.Embed(
                title="📚 あなたの単語帳",
                color=0x2b90d9
            )
            
            for i, nb in enumerate(notebooks, 1):
                auto_label = " (自動更新)" if nb['is_auto'] else ""
                value = f"{nb['word_count']}語"
                if nb['description']:
                    value += f"\n{nb['description']}"
                embed.add_field(
                    name=f"{i}. 📖 {nb['name']}{auto_label}",
                    value=value,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await ErrorHandler.handle_interaction_error(
                interaction,
                e,
                log_context="notebook.notebook_list"
            )

    @discord.app_commands.command(
        name="notebook_list_system",
        description="システム推奨単語帳の一覧を表示"
    )
    async def notebook_list_system(self, interaction: discord.Interaction) -> None:
        """システム推奨単語帳一覧を表示"""
        try:
            db_manager = get_db_manager()
            async with db_manager.acquire() as conn:
                notebooks = await conn.fetch("""
                    SELECT 
                        n.notebook_id,
                        n.name,
                        n.description,
                        COUNT(snw.word_id) as word_count
                    FROM vocabulary_notebooks n
                    LEFT JOIN system_notebook_words snw ON n.notebook_id = snw.notebook_id
                    WHERE n.is_system = TRUE
                    GROUP BY n.notebook_id, n.name, n.description
                    ORDER BY n.created_at DESC
                """)
            
            if not notebooks:
                await interaction.response.send_message(
                    "📚 システム推奨単語帳がまだありません。",
                    ephemeral=True
                )
                return
            
            # Embedで表示
            embed = discord.Embed(
                title="📚 システム推奨単語帳",
                description="全ユーザーが利用できる標準的な単語帳です。",
                color=0x2b90d9
            )
            
            for i, nb in enumerate(notebooks, 1):
                value = f"{nb['word_count']}語"
                if nb['description']:
                    value += f"\n{nb['description']}"
                embed.add_field(
                    name=f"{i}. ⭐ {nb['name']}",
                    value=value,
                    inline=False
                )
            
            embed.set_footer(text="💡 /notebook_study で学習できます")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await ErrorHandler.handle_interaction_error(
                interaction,
                e,
                log_context="notebook.notebook_list_system"
            )

    @discord.app_commands.command(
        name="notebook_delete",
        description="単語帳を削除"
    )
    async def notebook_delete(
        self,
        interaction: discord.Interaction,
        name: str
    ) -> None:
        """単語帳を削除"""
        user_id = str(interaction.user.id)
        
        try:
            db_manager = get_db_manager()
            async with db_manager.acquire() as conn:
                # 単語帳を取得
                notebook = await conn.fetchrow("""
                    SELECT notebook_id FROM vocabulary_notebooks 
                    WHERE user_id = $1 AND name = $2
                """, user_id, name)
                
                if not notebook:
                    await interaction.response.send_message(
                        f"❌ 単語帳「{name}」が見つかりません。",
                        ephemeral=True
                    )
                    return
                
                # 削除（CASCADEでnotebook_wordsも削除される）
                await conn.execute("""
                    DELETE FROM vocabulary_notebooks 
                    WHERE notebook_id = $1
                """, notebook['notebook_id'])
            
            await interaction.response.send_message(
                f"✅ 単語帳「{name}」を削除しました。",
                ephemeral=True
            )
            logger.info(f"ユーザー {user_id} が単語帳「{name}」を削除しました")
        except Exception as e:
            await ErrorHandler.handle_interaction_error(
                interaction,
                e,
                log_context="notebook.notebook_delete"
            )

    @discord.app_commands.command(
        name="notebook_add",
        description="単語帳に単語を追加"
    )
    async def notebook_add(
        self,
        interaction: discord.Interaction,
        notebook_name: str,
        word: str
    ) -> None:
        """単語帳に単語を追加"""
        user_id = str(interaction.user.id)
        
        try:
            db_manager = get_db_manager()
            async with db_manager.acquire() as conn:
                # 単語帳を取得
                notebook = await conn.fetchrow("""
                    SELECT notebook_id FROM vocabulary_notebooks 
                    WHERE user_id = $1 AND name = $2
                """, user_id, notebook_name)
                
                if not notebook:
                    await interaction.response.send_message(
                        f"❌ 単語帳「{notebook_name}」が見つかりません。",
                        ephemeral=True
                    )
                    return
                
                # 単語を検索（部分一致でも検索できるように）
                word_row = await conn.fetchrow("""
                    SELECT word_id, word, jp FROM words 
                    WHERE word ILIKE $1 
                    LIMIT 1
                """, word)
                
                if not word_row:
                    # 前方一致で再試行
                    word_row = await conn.fetchrow("""
                        SELECT word_id, word, jp FROM words 
                        WHERE word ILIKE $1 || '%'
                        LIMIT 1
                    """, word)
                
                if not word_row:
                    await interaction.response.send_message(
                        f"❌ 単語「{word}」が見つかりません。\n"
                        "英単語を正確に入力してください。",
                        ephemeral=True
                    )
                    return
                
                # 既に追加されているかチェック
                existing = await conn.fetchrow("""
                    SELECT * FROM notebook_words 
                    WHERE notebook_id = $1 AND word_id = $2
                """, notebook['notebook_id'], word_row['word_id'])
                
                if existing:
                    await interaction.response.send_message(
                        f"✅ 単語「{word_row['word']}」は既に単語帳に追加されています。",
                        ephemeral=True
                    )
                    return
                
                # 追加
                await conn.execute("""
                    INSERT INTO notebook_words (notebook_id, word_id)
                    VALUES ($1, $2)
                """, notebook['notebook_id'], word_row['word_id'])
            
            await interaction.response.send_message(
                f"✅ 単語「{word_row['word']} ({word_row['jp']})」を「{notebook_name}」に追加しました！",
                ephemeral=True
            )
            logger.info(f"ユーザー {user_id} が単語帳「{notebook_name}」に「{word_row['word']}」を追加しました")
        except Exception as e:
            await ErrorHandler.handle_interaction_error(
                interaction,
                e,
                log_context="notebook.notebook_add"
            )

    @discord.app_commands.command(
        name="notebook_remove",
        description="単語帳から単語を削除"
    )
    async def notebook_remove(
        self,
        interaction: discord.Interaction,
        notebook_name: str,
        word: str
    ) -> None:
        """単語帳から単語を削除"""
        user_id = str(interaction.user.id)
        
        try:
            db_manager = get_db_manager()
            async with db_manager.acquire() as conn:
                # 単語帳を取得
                notebook = await conn.fetchrow("""
                    SELECT notebook_id FROM vocabulary_notebooks 
                    WHERE user_id = $1 AND name = $2
                """, user_id, notebook_name)
                
                if not notebook:
                    await interaction.response.send_message(
                        f"❌ 単語帳「{notebook_name}」が見つかりません。",
                        ephemeral=True
                    )
                    return
                
                # 単語を検索
                word_row = await conn.fetchrow("""
                    SELECT word_id, word, jp FROM words 
                    WHERE word ILIKE $1 
                    LIMIT 1
                """, word)
                
                if not word_row:
                    await interaction.response.send_message(
                        f"❌ 単語「{word}」が見つかりません。",
                        ephemeral=True
                    )
                    return
                
                # 削除
                result = await conn.execute("""
                    DELETE FROM notebook_words 
                    WHERE notebook_id = $1 AND word_id = $2
                """, notebook['notebook_id'], word_row['word_id'])
                
                if result == "DELETE 0":
                    await interaction.response.send_message(
                        f"❌ 単語「{word_row['word']}」は単語帳に存在しません。",
                        ephemeral=True
                    )
                    return
            
            await interaction.response.send_message(
                f"✅ 単語「{word_row['word']} ({word_row['jp']})」を「{notebook_name}」から削除しました。",
                ephemeral=True
            )
            logger.info(f"ユーザー {user_id} が単語帳「{notebook_name}」から「{word_row['word']}」を削除しました")
        except Exception as e:
            await ErrorHandler.handle_interaction_error(
                interaction,
                e,
                log_context="notebook.notebook_remove"
            )

    @discord.app_commands.command(
        name="notebook_study",
        description="単語帳から学習を開始"
    )
    async def notebook_study(
        self,
        interaction: discord.Interaction,
        notebook_name: str
    ) -> None:
        """単語帳から学習を開始（システム推奨単語帳も含む）"""
        user_id = str(interaction.user.id)
        
        try:
            await ensure_defer(interaction)
            
            db_manager = get_db_manager()
            async with db_manager.acquire() as conn:
                # 単語帳を取得（システム推奨もユーザー個人のも含む）
                notebook = await conn.fetchrow("""
                    SELECT notebook_id, name, is_system 
                    FROM vocabulary_notebooks 
                    WHERE name = $1 
                      AND (
                          is_system = TRUE 
                          OR user_id = $2
                      )
                """, notebook_name, user_id)
                
                if not notebook:
                    await interaction.followup.send(
                        f"❌ 単語帳「{notebook_name}」が見つかりません。",
                        ephemeral=True
                    )
                    return
                
                # システム推奨単語帳の場合
                if notebook['is_system']:
                    words = await conn.fetch("""
                        SELECT w.word_id, w.word, w.jp, w.pos, w.example_en, w.example_ja, w.synonyms, w.derived
                        FROM system_notebook_words snw
                        JOIN words w ON snw.word_id = w.word_id
                        WHERE snw.notebook_id = $1
                        ORDER BY snw.order_index, random()
                        LIMIT 20
                    """, notebook['notebook_id'])
                else:
                    # ユーザー個人の単語帳の場合
                    words = await conn.fetch("""
                        SELECT w.word_id, w.word, w.jp, w.pos, w.example_en, w.example_ja, w.synonyms, w.derived
                        FROM notebook_words nw
                        JOIN words w ON nw.word_id = w.word_id
                        WHERE nw.notebook_id = $1
                        ORDER BY random()
                        LIMIT 20
                    """, notebook['notebook_id'])
                
                if not words or len(words) < 1:
                    await interaction.followup.send(
                        f"❌ 単語帳「{notebook_name}」に単語がありません。\n"
                        "`/notebook_add` で単語を追加してください。",
                        ephemeral=True
                    )
                    return
                
                # 10問に制限
                items = [dict(r) for r in words][:10]
                batch_id = str(uuid.uuid4())
                
                view = VocabSessionView(batch_id, items)
                embed = discord.Embed(
                    title=f"英単語 10問 - {notebook_name}",
                    description=f"単語帳「{notebook_name}」から{len(items)}問を出題します。"
                )
                await safe_edit(interaction, embed=embed, view=None)
                await view.send_current(interaction)
                
                # セッションバッチを記録
                await conn.execute("""
                    INSERT INTO session_batches(user_id, module, batch_id) 
                    VALUES($1, $2, $3) 
                    ON CONFLICT DO NOTHING
                """, user_id, "vocab", batch_id)
                
                self.bot._vocab_session = view
                logger.info(f"ユーザー {user_id} が単語帳「{notebook_name}」から学習を開始しました")
        except Exception as e:
            await ErrorHandler.handle_interaction_error(
                interaction,
                e,
                log_context="notebook.notebook_study"
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Notebook(bot))
