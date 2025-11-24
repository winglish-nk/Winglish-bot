# Railwayでスクリプトを実行する方法

システム推奨単語帳を作成するスクリプトをRailwayで実行する方法を説明します。

---

## 🚀 方法1: Railway CLIを使用（推奨）

### 1. Railway CLIのインストール

**macOSの場合:**
```bash
brew install railway
```

**npmを使用する場合:**
```bash
npm i -g @railway/cli
```

### 2. Railwayにログイン

```bash
railway login
```

ブラウザが開いてログインを求められます。

### 3. プロジェクトをリンク

```bash
cd /tmp/Winglish-bot
railway link
```

プロジェクト一覧が表示されるので、`Winglish-bot`プロジェクトを選択します。

### 4. スクリプトを実行

```bash
railway run python scripts/create_system_notebooks.py
```

これで、Railwayの環境変数（`DATABASE_PUBLIC_URL`など）が自動的に読み込まれてスクリプトが実行されます。

---

## 🚀 方法2: Bot起動時に自動実行（簡単）

Botの起動時にシステム推奨単語帳が存在しない場合、自動的に作成するようにできます。

`main.py`の`setup_hook`に追加する方法：

```python
async def setup_hook(self) -> None:
    # ... 既存のコード ...
    
    # システム推奨単語帳の作成（存在しない場合のみ）
    await self.ensure_system_notebooks()
```

ただし、この方法は起動時に毎回チェックが走るため、パフォーマンスへの影響を考慮する必要があります。

---

## 🚀 方法3: 管理コマンドとして追加

Discordコマンドとして追加し、管理者が実行できるようにする方法：

```python
@discord.app_commands.command(name="admin_create_system_notebooks")
@commands.has_permissions(administrator=True)
async def admin_create_system_notebooks(self, interaction: discord.Interaction):
    """システム推奨単語帳を作成（管理者のみ）"""
    # ... 実装 ...
```

---

## 📝 推奨方法

**最も簡単で安全な方法は「方法1: Railway CLIを使用」です。**

1. Railway CLIをインストール
2. `railway link`でプロジェクトをリンク
3. `railway run python scripts/create_system_notebooks.py`で実行

これで、Railwayの環境変数が自動的に読み込まれ、リモートで安全に実行できます。

