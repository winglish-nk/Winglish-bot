# 🔑 GitHub Personal Access Token (PAT) の取得方法

GitHubにコードをプッシュする際に、認証エラーが発生した場合は、Personal Access Token (PAT) を使用します。

---

## 📋 手順

### 1. GitHubにログイン

1. **GitHub**にアクセス: https://github.com
2. **ログイン**します

### 2. Settings（設定）を開く

1. 右上の**プロフィール画像**をクリック
2. ドロップダウンメニューから**「Settings」**をクリック

### 3. Developer settings（開発者設定）を開く

1. 左サイドバーの一番下にある**「Developer settings」**をクリック
2. もしくは、直接アクセス: https://github.com/settings/apps

### 4. Personal access tokens（個人アクセストークン）を開く

1. 左サイドバーから**「Personal access tokens」**をクリック
2. **「Tokens (classic)」**をクリック
3. もしくは、直接アクセス: https://github.com/settings/tokens

### 5. 新しいトークンを生成

1. **「Generate new token」**をクリック
2. **「Generate new token (classic)」**を選択

### 6. トークンの設定

1. **「Note」**（メモ）: 用途を記入（例: `Winglish-bot-push`）
2. **「Expiration」**（有効期限）: 
   - `90 days`（90日間）
   - または `No expiration`（無期限）
3. **「Select scopes」**（スコープ選択）:
   - ✅ **`repo`** - リポジトリへのフルアクセス（**必須**）
   - ✅ **`workflow`** - GitHub Actionsのワークフローファイルを更新する場合（オプション）

### 7. トークンを生成してコピー

1. ページの一番下にある**「Generate token」**ボタンをクリック
2. **生成されたトークンが表示されます**（例: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
3. **⚠️ 重要**: このトークンは**この時だけ表示**されます。後で確認できません！
4. **すぐにコピー**してください

---

## 🔒 セキュリティ注意事項

- **トークンは秘密情報です**。他人に共有しないでください
- **トークンを漏洩した場合**、すぐにGitHubで無効化してください
- **トークンをコードやリポジトリに保存しない**でください
- **定期的にトークンを更新**してください（90日間の有効期限を推奨）

---

## 📝 トークンを使用してプッシュする方法

トークンを取得したら、以下のいずれかの方法でプッシュできます：

### 方法1: 一時的にURLに埋め込む（推奨）

```bash
cd /tmp/Winglish-bot
TOKEN=<コピーしたPAT>
git remote set-url origin https://winglish-nk:$TOKEN@github.com/winglish-nk/Winglish-bot.git
git push origin main
git remote set-url origin https://github.com/winglish-nk/Winglish-bot.git  # トークンをURLから削除
```

### 方法2: プッシュ時に認証情報を入力

```bash
cd /tmp/Winglish-bot
git push origin main
# Username: winglish-nk
# Password: <コピーしたPAT>  （パスワードの代わりにPATを入力）
```

---

## 🔍 トラブルシューティング

### エラー: `remote: Permission to winglish-nk/Winglish-bot.git denied`

**原因**: 認証に失敗しています

**解決方法**:
1. PATが正しくコピーされているか確認
2. PATに`repo`スコープが含まれているか確認
3. PATの有効期限が切れていないか確認

### エラー: `fatal: unable to access 'https://github.com/...': The requested URL returned error: 403`

**原因**: PATが無効か、権限が不足しています

**解決方法**:
1. PATが正しく設定されているか確認
2. PATに`repo`スコープが含まれているか確認
3. 新しいPATを生成して再試行

---

## 📋 チェックリスト

- [ ] GitHubにログインしている
- [ ] Settings > Developer settings > Personal access tokens > Tokens (classic) にアクセス
- [ ] 「Generate new token (classic)」をクリック
- [ ] Noteに用途を記入
- [ ] 有効期限を設定（90 days または No expiration）
- [ ] `repo`スコープをチェック（必須）
- [ ] `workflow`スコープをチェック（GitHub Actionsを使用する場合）
- [ ] 「Generate token」をクリック
- [ ] 生成されたトークンをコピー
- [ ] トークンを安全に保管

---

## 💡 次のステップ

PATを取得したら、`docs/guides/repository-migration.md` の「4. Personal Access Token (PAT) でプッシュする方法」セクションを参照して、プッシュしてください。

