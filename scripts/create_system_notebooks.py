#!/usr/bin/env python3
"""
システム推奨単語帳を作成するスクリプト

既存のNGSLデータ（wordsテーブル）から、システム推奨単語帳を作成します。
- 中学英単語 Level 1, 2（level 1, 2）
- 高校単語・入試必須 Level 3-10（level 3-10、各レベルごと）
- 大学受験必須単語（level 3以上全て、高校単語・入試必須）
"""

import asyncio
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# .envファイルを読み込む
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from db import get_db_manager, init_db


async def check_words_data() -> None:
    """wordsテーブルのデータを確認"""
    print("📊 wordsテーブルのデータを確認中...")
    
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # 全体の単語数
        total = await conn.fetchval("SELECT COUNT(*) FROM words")
        print(f"  全体の単語数: {total}語")
        
        # level別の単語数
        level_counts = await conn.fetch("""
            SELECT level, COUNT(*) as count 
            FROM words 
            WHERE level IS NOT NULL
            GROUP BY level 
            ORDER BY level
        """)
        
        if level_counts:
            print("  Level別の単語数:")
            for row in level_counts:
                print(f"    Level {row['level']}: {row['count']}語")
        else:
            print("  ⚠️ Level別のデータが見つかりませんでした")
        
        # 実際のlevelの値
        levels = await conn.fetch("SELECT DISTINCT level FROM words WHERE level IS NOT NULL ORDER BY level")
        if levels:
            level_values = [r['level'] for r in levels]
            print(f"  存在するLevel: {level_values}")
        else:
            print("  ⚠️ levelフィールドが設定されていない単語があります")


async def create_system_notebooks() -> None:
    """
    システム推奨単語帳を作成
    
    注意: 既存のwordsテーブル（NGSLの3800語）から単語を選ぶ
    新しい単語データは追加しない
    """
    print("\n🚀 システム推奨単語帳を作成します...\n")
    
    # データ確認
    await check_words_data()
    
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # 既存のシステム推奨単語帳を確認
        existing = await conn.fetch("""
            SELECT notebook_id, name, system_type 
            FROM vocabulary_notebooks 
            WHERE is_system = TRUE
        """)
        
        if existing:
            print(f"\n⚠️ 既存のシステム推奨単語帳が{len(existing)}個見つかりました:")
            for nb in existing:
                print(f"  - {nb['name']} ({nb['system_type']})")
            response = input("\n既存のシステム推奨単語帳を削除して再作成しますか？ (y/N): ")
            if response.lower() != 'y':
                print("❌ 作成をキャンセルしました")
                return
            
            # 既存のシステム推奨単語帳を削除（CASCADEでsystem_notebook_wordsも削除される）
            await conn.execute("DELETE FROM vocabulary_notebooks WHERE is_system = TRUE")
            print("✅ 既存のシステム推奨単語帳を削除しました")
        
        print("\n📚 システム推奨単語帳を作成中...\n")
        
        # 中学英単語 Level 1を作成
        print("1. 中学英単語 Level 1を作成中...")
        notebook_id_1 = await conn.fetchval("""
            INSERT INTO vocabulary_notebooks (user_id, name, description, is_system, system_type)
            VALUES (NULL, '中学英単語 Level 1', '中学英単語（level 1）', TRUE, 'ngsl_level1')
            RETURNING notebook_id
        """)
        
        # Level 1の単語を追加
        result_1 = await conn.execute("""
            INSERT INTO system_notebook_words (notebook_id, word_id, order_index)
            SELECT $1, word_id, row_number() OVER (ORDER BY word_id) as order_index
            FROM words 
            WHERE level = 1 
            ORDER BY word_id
        """, notebook_id_1)
        
        count_1 = await conn.fetchval("""
            SELECT COUNT(*) FROM system_notebook_words WHERE notebook_id = $1
        """, notebook_id_1)
        print(f"   ✅ 中学英単語 Level 1を作成しました（{count_1}語）")
        
        # 中学英単語 Level 2を作成
        print("2. 中学英単語 Level 2を作成中...")
        notebook_id_2 = await conn.fetchval("""
            INSERT INTO vocabulary_notebooks (user_id, name, description, is_system, system_type)
            VALUES (NULL, '中学英単語 Level 2', '中学英単語（level 2）', TRUE, 'ngsl_level2')
            RETURNING notebook_id
        """)
        
        result_2 = await conn.execute("""
            INSERT INTO system_notebook_words (notebook_id, word_id, order_index)
            SELECT $1, word_id, row_number() OVER (ORDER BY word_id) as order_index
            FROM words 
            WHERE level = 2 
            ORDER BY word_id
        """, notebook_id_2)
        
        count_2 = await conn.fetchval("""
            SELECT COUNT(*) FROM system_notebook_words WHERE notebook_id = $1
        """, notebook_id_2)
        print(f"   ✅ 中学英単語 Level 2を作成しました（{count_2}語）")
        
        # 高校単語・入試必須 Level 3-10を作成（動的に各レベルを作成）
        max_level = await conn.fetchval("SELECT MAX(level) FROM words WHERE level IS NOT NULL")
        
        if max_level and max_level >= 3:
            print(f"3. 高校単語・入試必須 Level 3-{max_level}を作成中...")
            
            # Level 3から最大レベルまで、各レベルごとに単語帳を作成
            for level in range(3, max_level + 1):
                level_count = await conn.fetchval("SELECT COUNT(*) FROM words WHERE level = $1", level)
                if level_count and level_count > 0:
                    notebook_id_level = await conn.fetchval("""
                        INSERT INTO vocabulary_notebooks (user_id, name, description, is_system, system_type)
                        VALUES (NULL, $1, $2, TRUE, $3)
                        RETURNING notebook_id
                    """, 
                    f'高校単語・入試必須 Level {level}',
                    f'高校単語・入試必須（level {level}）',
                    f'ngsl_level{level}')
                    
                    await conn.execute("""
                        INSERT INTO system_notebook_words (notebook_id, word_id, order_index)
                        SELECT $1, word_id, row_number() OVER (ORDER BY word_id) as order_index
                        FROM words 
                        WHERE level = $2 
                        ORDER BY word_id
                    """, notebook_id_level, level)
                    
                    count_level = await conn.fetchval("""
                        SELECT COUNT(*) FROM system_notebook_words WHERE notebook_id = $1
                    """, notebook_id_level)
                    print(f"   ✅ 高校単語・入試必須 Level {level}を作成しました（{count_level}語）")
        else:
            print("   ⚠️ Level 3以上の単語が見つかりませんでした（スキップ）")
        
        # 「大学受験必須単語」を作成（level 3以上から選ぶ、高校単語・入試必須）
        print(f"\n4. 大学受験必須単語を作成中（level 3-{max_level if max_level else 10}から選択）...")
        level_3plus_count = await conn.fetchval("SELECT COUNT(*) FROM words WHERE level >= 3")
        if level_3plus_count and level_3plus_count > 0:
            notebook_id_target = await conn.fetchval("""
                INSERT INTO vocabulary_notebooks (user_id, name, description, is_system, system_type)
                VALUES (NULL, '大学受験必須単語', '大学受験に必要な高校単語・入試必須語（level 3以上から選択）', TRUE, 'entrance_exam_essential')
                RETURNING notebook_id
            """)
            
            # level 3以上から全ての単語を選ぶ（高校単語・入試必須）
            await conn.execute("""
                INSERT INTO system_notebook_words (notebook_id, word_id, order_index)
                SELECT $1, word_id, row_number() OVER (ORDER BY level, word_id) as order_index
                FROM words 
                WHERE level >= 3
                ORDER BY level, word_id
            """, notebook_id_target)
            
            count_target = await conn.fetchval("""
                SELECT COUNT(*) FROM system_notebook_words WHERE notebook_id = $1
            """, notebook_id_target)
            print(f"   ✅ 大学受験必須単語を作成しました（{count_target}語）")
        else:
            print("   ⚠️ Level 3以上の単語が見つかりませんでした（スキップ）")
    
    print("\n✅ システム推奨単語帳の作成が完了しました！")


async def main() -> None:
    """メイン関数"""
    try:
        # データベース接続を初期化
        db_manager = get_db_manager()
        await db_manager.initialize()
        print("✅ データベース接続完了")
        
        # システム推奨単語帳を作成
        await create_system_notebooks()
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

