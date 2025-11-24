# 変更履歴

このファイルには、プロジェクトへの重要な変更が記録されます。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) に基づいており、このプロジェクトは [Semantic Versioning](https://semver.org/lang/ja/) に従います。

## [未リリース]

### 追加
- 環境変数検証機能の追加（起動時の自動チェック）
- 統一されたエラーハンドリング（`error_handler.py`）
- データベース接続管理の改善（`DatabaseManager`クラス）
- 型ヒントの追加（すべての関数とクラス）
- テストコードの追加（pytest）
- CI/CDパイプライン（GitHub Actions）
- ロギング設定の改善（構造化ログ、ファイル出力）
- 設定管理クラス（`settings.py`）
- 入力値バリデーション（`validators.py`）
- セキュリティチェックリスト（`SECURITY_CHECKLIST.md`）
- コントリビューションガイドライン（`CONTRIBUTING.md`）
- `.env.example`ファイル（環境変数設定のテンプレート）

### 改善
- READMEの更新（プロジェクト構造、テスト方法、改善履歴を追加）
- データベース接続の一元管理
- エラーメッセージの改善（ユーザーフレンドリーなメッセージ）
- コードの可読性向上（型ヒント、docstring）

### セキュリティ
- SQLインジェクション対策（パラメータ化クエリの使用）
- 入力値のバリデーションとサニタイズ
- 環境変数の適切な管理（`.gitignore`による保護）

---

## 改善の詳細

各改善の詳細については、以下のドキュメントを参照してください：
- `docs/guides/IMPROVEMENTS_BENEFITS.md` - 改善による効果
- `docs/guides/IMPROVEMENTS_EXAMPLES.md` - 改善前後のコード比較
- `SECURITY_CHECKLIST.md` - セキュリティ対策の詳細

---

## [未リリース] 最新の変更

### 改善
- Lintワークフローの追加と安定化（ruff、mypy）
- ドキュメントの整理（`docs/guides/`配下に統合）
- READMEの関連ドキュメントセクションを整理・更新

### 変更
- ドキュメントファイルを`docs/guides/`配下に移動
  - `IMPROVEMENTS_BENEFITS.md` → `docs/guides/IMPROVEMENTS_BENEFITS.md`
  - `IMPROVEMENTS_EXAMPLES.md` → `docs/guides/IMPROVEMENTS_EXAMPLES.md`
  - `DB_USAGE_GUIDE.md` → `docs/guides/DB_USAGE_GUIDE.md`

