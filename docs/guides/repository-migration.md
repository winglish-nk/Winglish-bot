# リポジトリ移行とPATによるプッシュ手順

このドキュメントでは、Winglish Bot のコードを `winglish-nk/Winglish-bot` リポジトリへ移行するときの手順、Railway との接続更新、Personal Access Token (PAT) を使ったプッシュ方法をまとめています。

---

## 1. GitHub リポジトリを準備する
1. `winglish-nk` アカウントで GitHub にログイン
2. https://github.com/new にアクセス
3. Repository name: `Winglish-bot`
4. Description: 「大学受験英語サービス Discord Bot」（任意）
5. Public/Private を選択
6. **Initialize this repository with a README** のチェックを外す
7. **Create repository** をクリック

---

## 2. リモート URL を変更してプッシュ
```bash
cd /tmp/Winglish-bot
# 現在の設定を確認
git remote -v

# 新しいリモートに変更
NEW_REMOTE=https://github.com/winglish-nk/Winglish-bot.git
git remote set-url origin "$NEW_REMOTE"

# main ブランチをプッシュ
git push -u origin main
```
必要に応じて他のブランチも `git push -u origin <branch>` で公開します。

> 参考: 旧 `migrate_to_winglish-nk.sh` で行っていた作業を上記のコマンドにまとめました。

---

## 3. Railway の接続を更新
1. Railway ダッシュボードで対象プロジェクトを開く
2. **Settings → Source** を開き、既存の接続があれば **Disconnect**
3. **Connect GitHub repo** をクリックし `winglish-nk/Winglish-bot` を選択
4. `main` ブランチを指定してデプロイ

環境変数（DISCORD_TOKEN 等）は Railway の **Variables** タブで必ず再設定してください。

---

## 4. Personal Access Token (PAT) でプッシュする方法
HTTPS でプッシュする際に認証エラーが出る場合は PAT を利用します。

### 4.1 トークンを作成
1. GitHub → **Settings** → **Developer settings**
2. **Personal access tokens** → **Tokens (classic)**
3. **Generate new token** をクリック
4. Note: `Winglish-bot-push` など
5. Expiration: 90 days または No expiration
6. Scopes: `repo`（必要なら `workflow` も）
7. Generate して表示されたトークンをコピー（再表示不可）

### 4.2 認証情報として使用
- **方法A（その場で入力）**
  ```bash
  git push -u origin main
  # Username: winglish-nk
  # Password: <コピーしたPAT>
  ```
- **方法B（URLに一時的に埋め込む）**
  ```bash
  TOKEN=<PAT>
  git remote set-url origin https://winglish-nk:$TOKEN@github.com/winglish-nk/Winglish-bot.git
  git push -u origin main
  git remote set-url origin https://github.com/winglish-nk/Winglish-bot.git
  ```
- **方法C（credential helperを使う）**
  ```bash
  git credential-osxkeychain store
  # Username: winglish-nk
  # Password: <PAT>
  git push -u origin main
  ```

*セキュリティ注意*: トークンを `.env` やリポジトリに保存しないでください。漏洩した場合は即座に GitHub で revoke してください。

---

## 5. トラブルシューティング
| エラー | 対処 |
| --- | --- |
| `Repository not found` | リポジトリがまだ存在しない。手順1で作成する |
| `Permission denied` | 認証が必要。PAT または SSH を利用する |
| `Authentication failed` | ユーザー名/トークンが正しいか確認し、再入力 |

---

## 6. 移行後の確認リスト
- [ ] https://github.com/winglish-nk/Winglish-bot にファイルが揃っている
- [ ] GitHub Actions (CI/Tests/Lint) が成功する
- [ ] Railway のデプロイが成功し、Bot が起動している
- [ ] Secrets や環境変数の設定漏れがない

これでリポジトリ移行に関する一時的な手順を一か所にまとめられました。更新が必要な場合は本ファイルを編集してください。
