# Winglish Discord Bot

> 🧠 **Winglish Discord Bot** は、英語学習サービス「[Winglish](https://winglish.site/)」を Discord 上で展開するために開発された学習支援Botです。  
> 英単語・英文解釈（SVOCM）・長文読解の3機能を通じて、チャット感覚で学習が進められます。

---

## プロジェクト概要

このBotはもともと、ノーコードツール **Bubble** 上で構築されていた「Winglish」を、  
Discord 環境でも利用できるように再設計したものです。

- **対象**：高校生〜大学生の英語学習者  
- **目的**：インプット型学習を脱して、チャットベースのアウトプット型英語学習を実現  
- **構成要素**
  - Discord Bot（`main.py` / `cogs/*`）
  - PostgreSQL（Railway上で運用）
  - Dify API（出題・採点処理）

---

## セットアップ手順

### 1. 環境準備

- **Python 3.12 以上**
- **Git / Railway / Discord Developer Portal アカウント**
- 任意：VSCode + Poetry or venv

```bash
git clone https://github.com/winglish-nk/Winglish-bot.git
cd Winglish-bot
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 2. `.env` 設定

`.env.example` ファイルをコピーして `.env` ファイルを作成し、実際の値を設定してください：

```bash
cp .env.example .env
```

その後、`.env` ファイルを編集して、実際の値を設定してください：

```dotenv
# Discord
DISCORD_TOKEN=あなたのBotトークン
TEST_GUILD_ID=テスト用サーバーID（オプション）

# Database
DATABASE_PUBLIC_URL=postgresql://user:password@host:port/database

# Dify API
DIFY_API_KEY_QUESTION=app-xxxxxxxx
DIFY_API_KEY_ANSWER=app-yyyyyyyy

# ロギング（オプション）
LOG_LEVEL=INFO
LOG_FILE=logs/winglish.log
```

> 📝 **ヒント**: `.env.example` ファイルには設定項目の詳細な説明が含まれています。参照してください。

> 🔒 **セキュリティ注意**  
> - BotトークンやAPIキーは `.env` と Railway Secrets のみに保存し、GitHubには絶対に公開しないでください
> - `.env` ファイルは `.gitignore` に含まれているため、Gitにはコミットされません
> - 公開リポジトリをそのまま利用する場合も、**各自の新しいBotを作成して運用**してください

> ✅ **環境変数の自動検証**  
> Bot起動時に必要な環境変数が設定されているか自動的にチェックします。設定が不足している場合は、起動時に分かりやすいエラーメッセージが表示されます。

---

### 3. データベース初期化

```bash
python apply_schema.py
python scripts/load_words.py
```

- `apply_schema.py`：`sql/schema.sql` を適用  
- `load_words.py`：CSVから単語データを投入  

---

### 4. Botを起動（ローカル）

```bash
python main.py
```

Botが起動し、Discord 上に「Winglish」メニューが表示されればOKです。

起動時に以下のようなログが表示されます：
```
2025-01-15 10:30:45 [INFO] winglish.db: ✅ データベース接続プールの初期化が完了しました
2025-01-15 10:30:46 [INFO] winglish: ✅ データベース初期化完了
2025-01-15 10:30:47 [INFO] winglish: ✅ Cog 読み込み完了: cogs.vocab
...
2025-01-15 10:30:48 [INFO] winglish: ✅ Logged in as Winglish Bot (123456789)
```

---

### 5. Railwayデプロイ

1. Railwayで新しいプロジェクトを作成  
2. GitHubリポジトリ（`winglish-nk/Winglish-bot`）を接続
3. PostgreSQLアドオンを追加  
4. **Variables** タブで環境変数を設定：
   - `DISCORD_TOKEN`
   - `DATABASE_PUBLIC_URL`（PostgreSQLアドオンを追加すると自動設定される）
   - `DIFY_API_KEY_QUESTION`
   - `DIFY_API_KEY_ANSWER`
   - その他の環境変数
5. デプロイが自動的に開始されます
6. **Logs** タブで `✅ Cog 読み込み完了` が出ればデプロイ成功

---

## コマンド例

| 機能 | コマンド / 操作 | 説明 |
|------|------------------|------|
| メニュー表示 | `/winglish menu` | 英単語・SVOCM・長文読解のメインメニューを表示 |
| 開始 | `/start` | 個人鍵チャンネルにメニューを送信 |
| 英単語 | 「英単語」ボタン | 10問テストを開始（SRS対応） |
| 英文解釈 | 「SVOCM」ボタン | 文型入力モーダルが開く |
| 長文読解 | 「長文読解」ボタン | 1問の長文を生成→4択×2設問を出題 |
| 管理 | `/winglish reset / attach_menu / ping / diag_vocab` | 管理用コマンド |

---

## テスト

### テストの実行

```bash
# すべてのテストを実行
pytest

# カバレッジレポート付きで実行
pytest --cov=. --cov-report=html

# 特定のテストファイルを実行
pytest tests/test_srs.py

# 詳細な出力で実行
pytest -v
```

### テストカバレッジ

カバレッジレポートは `htmlcov/index.html` で確認できます。

詳細は [tests/README.md](tests/README.md) を参照してください。

---

## 開発ガイド

### データベース接続

推奨される使用方法：

```python
from db import get_db_manager

db_manager = get_db_manager()
async with db_manager.acquire() as conn:
    result = await conn.fetch("SELECT * FROM users WHERE user_id = $1", user_id)
```

詳細は [DB_USAGE_GUIDE.md](DB_USAGE_GUIDE.md) を参照してください。

### エラーハンドリング

統一されたエラーハンドリングを使用：

```python
from error_handler import ErrorHandler

try:
    # 処理
except Exception as e:
    await ErrorHandler.handle_interaction_error(
        interaction,
        e,
        log_context="my_feature"
    )
```

### 型ヒント

すべての関数に型ヒントが追加されています。IDEの自動補完が効きます。

---

## 改善履歴

### 最近の改善

- ✅ **環境変数検証**: 起動時に必要な設定を自動チェック
- ✅ **エラーハンドリング**: 統一されたエラー処理で安定性向上
- ✅ **型ヒント**: コードの可読性と保守性向上
- ✅ **データベース接続**: DatabaseManagerクラスで一元管理
- ✅ **テストコード**: pytestによるテスト環境の構築
- ✅ **ロギング**: 構造化されたログで問題の早期発見

詳細は [IMPROVEMENTS_BENEFITS.md](IMPROVEMENTS_BENEFITS.md) を参照してください。

---

## 構成図（概要）

```mermaid
flowchart TD
  U[User] -->|Slash Command / Button| DC[Discord Server]
  DC -->|Gateway Events| WB[Winglish Bot]
  WB -->|/v1/workflows/run| DF[Dify API]
  subgraph Railway
    WB --- PG[(PostgreSQL)]
  end
```

---

## 技術スタック

- **Python 3.12+**
- **discord.py 2.4.0** - Discord Botライブラリ
- **asyncpg 0.29.0** - PostgreSQL非同期ドライバ
- **PostgreSQL** - データベース
- **Dify API** - AI出題・採点処理
- **pytest** - テストフレームワーク

---

## プロジェクト構造

```
Winglish-bot/
├── main.py                 # Botのエントリーポイント
├── config.py              # 環境変数の管理と検証
├── db.py                  # データベース接続管理（DatabaseManager）
├── error_handler.py       # 統一されたエラーハンドリング
├── srs.py                 # SRS（Spaced Repetition System）アルゴリズム
├── utils.py               # ユーティリティ関数
├── dify.py                # Dify API連携
├── cogs/                  # Botコマンドと機能
│   ├── vocab.py          # 英単語学習
│   ├── svocm.py          # 英文解釈（SVOCM）
│   ├── reading.py        # 長文読解
│   ├── menu.py           # メインメニュー
│   ├── onboarding.py     # オンボーディング
│   └── admin.py          # 管理コマンド
├── tests/                 # テストコード
├── sql/                   # データベーススキーマ
└── scripts/               # ユーティリティスクリプト
```

---

## 注意事項 / 開発方針

- **新しいBotを作成してください。**  
  このリポジトリのBotトークンは使用禁止です。各自の環境で新規登録して運用してください。
- **リポジトリのforkやPRは想定していません。**  
  コードを参考に個人環境で開発・改善してください。
- **既知の問題**
  - 鍵チャンネル作成時にユーザーネームが取得できないことがある  
  - 一部メッセージ遷移（英単語終了後など）に不安定な挙動あり  

---

## 関連ドキュメント

- [DB_USAGE_GUIDE.md](DB_USAGE_GUIDE.md) - データベース接続の使用方法
- [tests/README.md](tests/README.md) - テストの実行方法
- [IMPROVEMENTS_BENEFITS.md](IMPROVEMENTS_BENEFITS.md) - 改善による効果の説明
- [IMPROVEMENTS_EXAMPLES.md](IMPROVEMENTS_EXAMPLES.md) - 改善前後のコード比較
- [docs/guides/environment-and-error-handling.md](docs/guides/environment-and-error-handling.md) - 環境変数管理とエラーハンドリングの詳細
- [docs/guides/repository-migration.md](docs/guides/repository-migration.md) - リポジトリ移行とPAT利用の手順
- [docs/guides/roadmap.md](docs/guides/roadmap.md) - 今後の改善アイデアと優先タスク

---

## 🌟 開発者メモ

- 作者：國政 蒼矢（Tokyo International Professional University of Technology）  
- 環境：Windows 11 / Python 3.12 / Railway
- リポジトリ：https://github.com/winglish-nk/Winglish-bot
