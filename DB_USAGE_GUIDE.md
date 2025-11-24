# データベース接続の使用方法ガイド

## 📚 概要

`db.py`には`DatabaseManager`クラスが実装されており、データベース接続を一元管理できます。

## 🎯 推奨される使用方法

### 方法1: DatabaseManagerを直接使用（推奨）

```python
from db import get_db_manager

# DatabaseManagerインスタンスを取得
db_manager = get_db_manager()

# コンテキストマネージャーで接続を取得（推奨）
async with db_manager.acquire() as conn:
    result = await conn.fetch("SELECT * FROM users WHERE user_id = $1", user_id)
    # 自動的に接続が返却される
```

**メリット:**
- ✅ 接続のライフサイクルが明確
- ✅ 接続リークを防げる
- ✅ エラーハンドリングが容易

### 方法2: 既存のget_pool()を使用（後方互換性）

```python
from db import get_pool

# 接続プールを取得
pool = await get_pool()

# コンテキストマネージャーで接続を取得
async with pool.acquire() as conn:
    result = await conn.fetch("SELECT * FROM users WHERE user_id = $1", user_id)
```

**注意:**
- 既存コードとの互換性のため残されています
- 新しいコードでは`DatabaseManager`の使用を推奨します

## 🔍 DatabaseManagerの主な機能

### 1. 接続の取得

```python
from db import get_db_manager

db_manager = get_db_manager()

# コンテキストマネージャー（推奨）
async with db_manager.acquire() as conn:
    users = await conn.fetch("SELECT * FROM users")

# プールを直接使用（非推奨）
pool = db_manager.pool
async with pool.acquire() as conn:
    users = await conn.fetch("SELECT * FROM users")
```

### 2. ヘルスチェック

```python
from db import get_db_manager

db_manager = get_db_manager()
is_healthy = await db_manager.health_check()

if not is_healthy:
    logger.error("データベース接続に問題があります")
```

### 3. 接続の閉鎖

```python
from db import close_db

# アプリケーション終了時
await close_db()
```

## 📝 実装例

### Cogでの使用例

```python
from db import get_db_manager
from error_handler import ErrorHandler

class MyCog(commands.Cog):
    async def get_user(self, interaction: discord.Interaction, user_id: str):
        try:
            db_manager = get_db_manager()
            async with db_manager.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM users WHERE user_id = $1",
                    user_id
                )
            if row:
                await interaction.send(f"ユーザー: {row['name']}")
            else:
                await interaction.send("ユーザーが見つかりません")
        except Exception as e:
            await ErrorHandler.handle_interaction_error(
                interaction,
                e,
                log_context="MyCog.get_user"
            )
```

## ⚙️ 設定

### 接続プールの設定

`main.py`の`init_db()`を呼び出す前に、以下のように設定できます：

```python
from db import get_db_manager

db_manager = get_db_manager()
await db_manager.initialize(
    min_size=2,      # 最小接続数（デフォルト: 1）
    max_size=20,     # 最大接続数（デフォルト: 10）
    command_timeout=120  # タイムアウト（秒、デフォルト: 60）
)
```

## 🔄 既存コードからの移行

### 移行前

```python
from db import get_pool

pool = await get_pool()
async with pool.acquire() as con:
    result = await con.fetch("SELECT * FROM users")
```

### 移行後（推奨）

```python
from db import get_db_manager

db_manager = get_db_manager()
async with db_manager.acquire() as conn:
    result = await conn.fetch("SELECT * FROM users")
```

### 移行の優先度

1. **高優先度**: 新しく作成するコード
2. **中優先度**: 頻繁に使用されるCog
3. **低優先度**: 既存の安定したコード（後方互換性を維持）

## 🚨 注意事項

1. **接続の適切な解放**
   - 必ず`async with`を使用してください
   - 手動で接続を取得する場合は、必ず返却してください

2. **エラーハンドリング**
   - データベースエラーは`error_handler.py`で処理してください
   - 接続エラーは自動的にリトライされません（今後の拡張予定）

3. **接続プールサイズ**
   - デフォルトのmax_size=10で十分な場合がほとんどです
   - 大量の同時リクエストがある場合は調整を検討してください

## 📊 パフォーマンス

- 接続プールにより、接続の再利用が可能
- 最小接続数（min_size）を設定することで、常に利用可能な接続を保持
- 最大接続数（max_size）を超えた場合、接続が利用可能になるまで待機

## 🔗 関連ファイル

- `db.py`: DatabaseManagerクラスの実装
- `error_handler.py`: データベースエラーの処理
- `config.py`: DATABASE_URLの設定

