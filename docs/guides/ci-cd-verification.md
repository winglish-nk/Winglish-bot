# CI/CD動作確認ガイド

このガイドでは、GitHub Actionsワークフローが正常に動作しているかを確認する方法を説明します。

---

## 確認方法

### 方法1: GitHub Actionsページで確認（最も簡単）

1. GitHubリポジトリにアクセス
   ```
   https://github.com/winglish-nk/Winglish-bot
   ```

2. **Actions**タブをクリック

3. 左側のワークフロー一覧から確認したいワークフローを選択：
   - **CI** - テストとカバレッジチェック
   - **Tests** - テスト実行（Codecov連携）
   - **Lint** - コード品質チェック（Ruff + MyPy）

4. 各ワークフローの実行履歴を確認：
   - ✅ **緑色のチェックマーク** = 正常に完了
   - ❌ **赤い×マーク** = エラーが発生
   - 🟡 **黄色の丸** = 実行中

5. 最新のコミット（`main`ブランチへのプッシュ）に対応する実行を確認

---

### 方法2: テストコミットをプッシュして確認

実際にワークフローがトリガーされるか確認する方法です：

1. **小さな変更を作成**（例：READMEに空白行を追加）

```bash
cd /tmp/Winglish-bot
echo "" >> README.md
git add README.md
git commit -m "test: CI/CD動作確認のためのテストコミット"
git push origin main
```

2. **GitHub Actionsページで実行状況を監視**
   - プッシュ後、数秒でワークフローが開始されます
   - 各ステップのログを確認できます

3. **完了まで待つ**（通常2-5分程度）
   - CI: テスト実行とカバレッジチェック
   - Tests: テスト実行とCodecovアップロード
   - Lint: Ruff と MyPy の実行

---

### 方法3: ワークフローファイルの構文チェック

ワークフローファイルに構文エラーがないか確認：

```bash
cd /tmp/Winglish-bot

# 各ワークフローファイルの構文を確認
cat .github/workflows/ci.yml | grep -E "name:|on:|jobs:" | head -10
cat .github/workflows/test.yml | grep -E "name:|on:|jobs:" | head -10
cat .github/workflows/lint.yml | grep -E "name:|on:|jobs:" | head -10
```

---

## 現在のワークフロー一覧

### 1. CI (`ci.yml`)
- **トリガー**: `push` と `pull_request` で `main` / `develop` ブランチ
- **実行内容**:
  - Python 3.12環境のセットアップ
  - 依存関係のインストール
  - 環境変数の検証
  - テスト実行（カバレッジ付き）
  - カバレッジが30%以上かチェック

### 2. Tests (`test.yml`)
- **トリガー**: `push` と `pull_request` で `main` / `develop` ブランチ
- **実行内容**:
  - テスト実行
  - Codecovへのカバレッジレポートアップロード

### 3. Lint (`lint.yml`)
- **トリガー**: `push` と `pull_request` で `main` / `develop` ブランチ
- **実行内容**:
  - Ruffによるコード品質チェック
  - MyPyによる型チェック

---

## トラブルシューティング

### ワークフローが実行されない

1. **ブランチ名を確認**
   - `main` または `develop` ブランチにプッシュしているか確認
   - 他のブランチではワークフローが実行されません

2. **ワークフローファイルのパスを確認**
   - `.github/workflows/*.yml` が正しい場所にあるか確認

3. **GitHub Actionsが有効か確認**
   - リポジトリのSettings → Actions → General で確認

### ワークフローが失敗する

1. **ログを確認**
   - 失敗したワークフローの実行ページでログを確認
   - エラーメッセージを確認して原因を特定

2. **よくある原因**
   - テストが失敗している
   - 依存関係のインストールエラー
   - 環境変数の設定不足
   - コードの構文エラー（Lintチェック）

### ローカルでテストを実行して確認

ワークフローが失敗する前に、ローカルでテストを実行：

```bash
# テスト実行
pytest -v

# Lintチェック
ruff check .

# 型チェック（エラーがあっても続行）
mypy . --ignore-missing-imports || true
```

---

## 推奨される確認フロー

1. **コードを変更したら**
   - ローカルでテストとLintを実行
   - 問題がなければコミット・プッシュ

2. **プッシュ後**
   - GitHub Actionsページで実行状況を確認
   - すべてのワークフローが✅になるまで待つ

3. **失敗した場合**
   - ログを確認してエラー原因を特定
   - ローカルで再現して修正
   - 再度プッシュして確認

---

## 参考リンク

- [GitHub Actions ドキュメント](https://docs.github.com/ja/actions)
- [リポジトリのActionsページ](https://github.com/winglish-nk/Winglish-bot/actions)
