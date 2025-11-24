#!/usr/bin/env python3
"""
データベースにシステム推奨単語帳用のカラムを追加するマイグレーションスクリプト
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

from db import get_db_manager


async def migrate() -> None:
    """システム推奨単語帳用のカラムを追加"""
    print("🔄 データベースマイグレーションを開始します...\n")
    
    db_manager = get_db_manager()
    await db_manager.initialize()
    
    async with db_manager.acquire() as conn:
        # vocabulary_notebooksテーブルのカラムを確認
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'vocabulary_notebooks'
            ORDER BY ordinal_position
        """)
        
        existing_columns = {row['column_name'] for row in columns}
        print("📊 既存のカラム:")
        for col in columns:
            print(f"  - {col['column_name']} ({col['data_type']})")
        
        # 不足しているカラムを追加
        print("\n🔧 不足しているカラムを追加中...\n")
        
        # user_idがNOT NULLの場合はNULLを許可
        if 'user_id' in existing_columns:
            try:
                await conn.execute("ALTER TABLE vocabulary_notebooks ALTER COLUMN user_id DROP NOT NULL")
                print("✅ user_idカラムをNULL許可に変更しました")
            except Exception as e:
                print(f"⚠️ user_idカラムの変更をスキップ: {e}")
        
        # is_systemカラムを追加
        if 'is_system' not in existing_columns:
            await conn.execute("ALTER TABLE vocabulary_notebooks ADD COLUMN is_system BOOLEAN DEFAULT FALSE")
            print("✅ is_systemカラムを追加しました")
        else:
            print("ℹ️ is_systemカラムは既に存在します")
        
        # system_typeカラムを追加
        if 'system_type' not in existing_columns:
            await conn.execute("ALTER TABLE vocabulary_notebooks ADD COLUMN system_type TEXT")
            print("✅ system_typeカラムを追加しました")
        else:
            print("ℹ️ system_typeカラムは既に存在します")
        
        # system_notebook_wordsテーブルを作成
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS system_notebook_words (
                    notebook_id INT NOT NULL REFERENCES vocabulary_notebooks(notebook_id) ON DELETE CASCADE,
                    word_id INT NOT NULL REFERENCES words(word_id) ON DELETE CASCADE,
                    order_index INT,
                    added_at TIMESTAMPTZ DEFAULT NOW(),
                    PRIMARY KEY(notebook_id, word_id)
                )
            """)
            print("✅ system_notebook_wordsテーブルを作成しました")
        except Exception as e:
            print(f"⚠️ system_notebook_wordsテーブルの作成をスキップ: {e}")
        
        # インデックスを作成
        try:
            await conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_system_notebook_name 
                ON vocabulary_notebooks(name) 
                WHERE is_system = TRUE
            """)
            print("✅ システム推奨単語帳用の一意インデックスを作成しました")
        except Exception as e:
            print(f"⚠️ インデックスの作成をスキップ: {e}")
        
        try:
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_system_notebook_words_notebook 
                ON system_notebook_words(notebook_id)
            """)
            print("✅ system_notebook_words用のインデックスを作成しました")
        except Exception as e:
            print(f"⚠️ インデックスの作成をスキップ: {e}")
        
        try:
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_system_notebook_words_word 
                ON system_notebook_words(word_id)
            """)
            print("✅ system_notebook_words用のインデックスを作成しました")
        except Exception as e:
            print(f"⚠️ インデックスの作成をスキップ: {e}")
    
    print("\n✅ マイグレーションが完了しました！")


async def main() -> None:
    """メイン関数"""
    try:
        await migrate()
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

