from __future__ import annotations

import logging
from typing import Optional

import discord
from discord.ext import commands

from db import get_db_manager
from error_handler import ErrorHandler
from utils import info_embed

logger = logging.getLogger('winglish.svocm')


class SvocmModal(discord.ui.Modal, title="SVOCM 解答"):
    s = discord.ui.TextInput(label="S", required=True)
    v = discord.ui.TextInput(label="V", required=True)
    o1 = discord.ui.TextInput(label="O1", required=False)
    o2 = discord.ui.TextInput(label="O2", required=False)
    c = discord.ui.TextInput(label="C", required=False)
    m = discord.ui.TextInput(label="M", required=False)

    def __init__(self, sentence_en: str, item_id: int) -> None:
        super().__init__()
        self.sentence_en: str = sentence_en
        self.item_id: int = item_id

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await interaction.response.defer(thinking=True, ephemeral=False)

            payload = {
                "inputs": {
                    "user_id": str(interaction.user.id),
                    "Question": self.sentence_en,
                    "Answer_S": str(self.s),
                    "Answer_V": str(self.v),
                    "Answer_O1": str(self.o1),
                    "Answer_O2": str(self.o2),
                    "Answer_C": str(self.c),
                    "Answer_M": str(self.m),
                    "question_id": str(self.item_id),
                    "training_type": "SVOCM"
                },
                "response_mode": "blocking",
                "user": str(interaction.user.id)
            }
            
            text = "（一時）SVOCMのDify採点は未設定です。ローカル採点で継続します。"

            # ログ保存
            try:
                db_manager = get_db_manager()
                async with db_manager.acquire() as conn:
                    await conn.execute("""
                      INSERT INTO study_logs(user_id, module, item_id, result)
                      VALUES($1,'svocm',$2,$3::jsonb)
                    """, str(interaction.user.id), int(self.item_id), {"feedback": text})
            except Exception as db_error:
                error_msg = await ErrorHandler.handle_database_error(
                    db_error,
                    "svocm.on_submit: ログ保存"
                )
                logger.error(f"ログ保存に失敗しましたが、採点結果は表示します: {db_error}")

            await interaction.followup.send(embed=discord.Embed(title="SVOCM 採点", description=text))
        except Exception as e:
            await ErrorHandler.handle_interaction_error(
                interaction,
                e,
                log_context="svocm.on_submit"
            )

class Svocm(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction) -> None:
        if interaction.type != discord.InteractionType.component:
            return
        cid = interaction.data.get("custom_id", "")
        if cid.startswith("svocm:pattern:"):
            pattern = int(cid.split(":")[-1])
            await self.show_item(interaction, pattern=pattern)
        elif cid == "svocm:random":
            await self.show_item(interaction, pattern=None)

    async def show_item(self, interaction: discord.Interaction, pattern: Optional[int]) -> None:
        try:
            try:
                db_manager = get_db_manager()
                async with db_manager.acquire() as conn:
                    if pattern:
                        row = await conn.fetchrow("SELECT * FROM svocm_items WHERE pattern=$1 ORDER BY random() LIMIT 1", pattern)
                    else:
                        row = await conn.fetchrow("SELECT * FROM svocm_items ORDER BY random() LIMIT 1")
            except Exception as db_error:
                error_msg = await ErrorHandler.handle_database_error(
                    db_error,
                    "svocm.show_item"
                )
                await ErrorHandler.safe_send_followup(
                    interaction,
                    error_msg,
                    ephemeral=True
                )
                return
            
            if not row:
                await ErrorHandler.safe_edit_message(
                    interaction,
                    embed=info_embed("英文解釈", "問題がありません（管理者に連絡してください）。"),
                    view=None
                )
                return

            sentence = row["sentence_en"]
            e = discord.Embed(
                title="SVOCM 問題",
                description=f"{sentence}\n\n（ヒントは ||スポイラー|| で運用可）"  
            )
            view = discord.ui.View()
            modal = SvocmModal(sentence, row["item_id"])
            # モーダル起動ボタン
            async def on_answer(i: discord.Interaction) -> None:
                try:
                    await i.response.send_modal(modal)
                except Exception as modal_error:
                    await ErrorHandler.handle_interaction_error(
                        i,
                        modal_error,
                        log_context="svocm.show_item: モーダル起動"
                    )
            btn = discord.ui.Button(label="解答する", style=discord.ButtonStyle.primary)
            btn.callback = on_answer
            view.add_item(btn)
            await ErrorHandler.safe_edit_message(interaction, embed=e, view=view)
        except Exception as e:
            await ErrorHandler.handle_interaction_error(
                interaction,
                e,
                log_context="svocm.show_item"
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Svocm(bot))
