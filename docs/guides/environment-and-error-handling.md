# 環境変数とエラーハンドリングのガイド

このドキュメントは、Winglish Bot における環境変数管理とエラーハンドリングの考え方・実装パターンをまとめたものです。README では触れきれない背景や設計理由を記録しています。

---

## 1. 環境変数のベストプラクティス

### なぜ環境変数を使うのか
- API トークンやデータベース接続情報などの機密情報をコードに埋め込まない
- 開発・ステージング・本番で設定値を切り替えやすい
- リポジトリを公開しても安全

### 推奨の管理方法
1. ローカル開発: `.env` ファイルに設定し、`python-dotenv` で読み込む
2. Railway 本番: `Variables` タブにキー/値を登録
3. 共有は `.env.example` のみ。具体的な値は共有しない

### 必須環境変数の自動検証
`config.py` の `validate_required_env()` が起動時に DISCORD_TOKEN や DATABASE_URL をチェックします。設定漏れがあると、以下のように丁寧なメッセージとともに起動を停止します。

```text
❌ エラー: 必要な環境変数が設定されていません
  - DISCORD_TOKEN
  - DATABASE_PUBLIC_URL または DATABASE_URL
```

この仕組みにより、Railway や GitHub Actions でも設定不足を即座に検知できます。

---

## 2. エラーハンドリング戦略

### 目的
- Bot が例外で停止しないようにする
- ユーザーには状況に応じた分かりやすいメッセージを返す
- ログに十分な情報を残して原因を特定しやすくする

### `error_handler.py` の役割
| メソッド | 役割 |
| --- | --- |
| `handle_interaction_error` | Discord とのやり取りで発生した例外を共通フォーマットで処理 |
| `safe_defer` / `safe_edit_message` / `safe_send_followup` | Interaction が応答済みかどうかを考慮しながら安全に操作を行う |
| `handle_database_error` | `asyncpg` の例外を分類し、ユーザー向けのメッセージを生成 |

### 代表的なエラー対応
- `discord.HTTPException(status=403)` → 「権限が不足しています」
- `discord.HTTPException(status=429)` → 「レート制限に達しました。少し待ってください」
- `asyncpg.PostgresConnectionError` → 「データベース接続エラー」
- その他 → 「予期しないエラー。管理者に連絡してください」

### 各 Cog での使い方
```python
from error_handler import ErrorHandler

try:
    ... # 正常処理
except Exception as exc:
    await ErrorHandler.handle_interaction_error(
        interaction,
        exc,
        log_context="vocab.start_ten"
    )
```

---

## 3. よくある質問

### Q. `.env` をコミットしてしまった場合は？
直ちに `git rm --cached .env` を実行し、GitHub トークンなどをローテーションしてください。

### Q. Discord/DB の資格情報が頻繁に変わる場合は？
Railway や GitHub Actions の Secrets で値を更新すれば、コードを変更せずに運用できます。

### Q. エラー内容をもっと細かくログに出したい
`logger.error(..., extra={...})` でユーザー ID などを付与しています。必要に応じて拡張してください。構造化ログ（JSON 形式）を使いたい場合は `logger_config.py` を参照して設定を追加できます。

---

## 4. 参考実装
- `config.py` … 環境変数の読み込みと検証
- `logger_config.py` … ログの初期化（ファイル出力を含む）
- `error_handler.py` … エラー処理と安全なレスポンス操作
- `cogs/` 各ファイル … `ErrorHandler` を利用した実装例

---

改善や疑問点があれば `docs/guides/environment-and-error-handling.md` を更新してください。
