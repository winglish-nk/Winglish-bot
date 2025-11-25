# 🔍 Botアプリケーションの見つけ方

## 現在の場所

もし**「Server Insights」**や**「Servers」**ページにいる場合は、**「Applications」**ページに移動する必要があります。

### 移動方法
1. 左上の**「← Back to Servers」**をクリック
2. 上部ナビゲーションバーの**「Applications」**をクリック

または直接アクセス:
- **Applications**: https://discord.com/developers/applications

---

## 問題: Discord Developer Portalでアプリケーションが表示されない

Discord Developer Portalの「Applications」ページが空の場合、以下の可能性があります：

1. **間違ったDiscordアカウントでログインしている**
2. **Botアプリケーションが別のアカウントで作成されている**
3. **Botアプリケーションが削除されている**

---

## ✅ 解決方法

### 方法1: 既存のBotアプリケーションを確認

現在のBot（Application ID: `1433634632053821593`）がどのアカウントで作成されたかを確認する必要があります。

**確認手順**:

1. **他のDiscordアカウントを確認**
   - Botを作成した可能性があるアカウントでログイン
   - Discord Developer Portalを開く
   - アプリケーション一覧を確認

2. **Botのトークンから確認**
   - Railwayの環境変数`DISCORD_TOKEN`を確認
   - Botのトークンがある場合、そのBotは既に存在します

3. **Railwayのログから確認**
   - Botが正常にログインしている場合、アプリケーションは存在します
   - ログ: `Logged in as Winglish#5862 (1433634632053821593)`

---

### 方法2: 新しいBotアプリケーションを作成

既存のBotアプリケーションが見つからない場合は、新しく作成する必要があります。

**作成手順**:

1. **Discord Developer Portal**を開く: https://discord.com/developers/applications
2. **「New Application」**をクリック
3. **アプリケーション名を入力**: 例「Winglish Bot」
4. **「Create」**をクリック
5. **左サイドバーから「Bot」**を選択
6. **「Add Bot」**をクリック
7. **「Reset Token」**をクリックしてトークンを取得
8. **「Copy」**をクリックしてトークンをコピー
9. **必要な権限を有効化**:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
   - ✅ Presence Intent
10. **左サイドバーから「OAuth2」** → **「URL Generator」**を選択
11. **Scopes**で以下をチェック:
    - ✅ `bot`
    - ✅ `applications.commands` ← **重要！**
12. **BOT PERMISSIONS**で必要な権限を選択
13. **生成されたURLをコピー**
14. **ブラウザでURLを開き、Botをサーバーに追加**
15. **Railwayの環境変数`DISCORD_TOKEN`を更新**

---

## 🔑 重要な確認事項

### Botアプリケーションが存在する場合

既存のBotアプリケーションが見つかった場合：

1. **Botのトークンを確認**
   - Discord Developer Portal > Bot > Token
   - Railwayの環境変数と一致しているか確認

2. **Botの権限を確認**
   - OAuth2 > URL Generator で `applications.commands` スコープが含まれているか
   - Botがサーバーに追加されているか

3. **Application IDを確認**
   - General Information > Application ID
   - ログのApplication IDと一致しているか確認

---

## ⚠️ 新規作成した場合の影響

**新しくBotアプリケーションを作成すると、既存のBotとは別物になります。**

### 新規作成の影響

1. **新しいApplication IDが生成される**
   - 既存: `1433634632053821593`
   - 新規: 別のID（例: `1234567890123456789`）

2. **新しいTokenが生成される**
   - Railwayの環境変数 `DISCORD_TOKEN` を更新する必要があります

3. **別のBotとして扱われる**
   - 既存のBotとデータが分かれる可能性があります
   - ただし、データベース内のデータ（ユーザー情報、学習履歴など）は影響を受けません
   - サーバー内のBot設定（権限、ロールなど）は再設定が必要です

4. **既存のBotは動作し続ける**
   - Railwayで既存のトークンを使い続ける限り、既存のBotは動作します
   - 新規作成しても、既存のBotは削除されません

### ✅ 推奨: まず既存のBotアプリケーションを探す

**新規作成する前に、以下の方法で既存のBotアプリケーションを探してください：**

1. **他のDiscordアカウントで確認**
   - インターンや他のメンバーが作成した可能性があります
   - 過去に使っていたDiscordアカウントを確認

2. **Railwayの環境変数を確認**
   - Railway > Winglish-botサービス > Variables
   - `DISCORD_TOKEN` の値を確認
   - このトークンを持つBotアプリケーションを探す

3. **Application IDで検索**
   - 既存のBot Application ID: `1433634632053821593`
   - このIDを持つBotアプリケーションの所有者を特定

4. **既存のBotアプリケーションが見つかった場合**
   - そのアカウントでDiscord Developer Portalにログイン
   - Bot設定を確認（特に `applications.commands` スコープ）
   - 必要に応じて、そのアカウントから現在のアカウントに権限を移行

---

## ⚠️ 注意事項

- **Botのトークンは秘密情報です**。他人に共有しないでください
- **トークンを漏洩した場合**、すぐに「Reset Token」で新しいトークンを生成してください
- **Botを削除すると**、すべての設定が失われます
- **新規作成する場合**、既存のBotとは別物になることを理解してください

---

## 📋 次のステップ

1. **まず既存のBotアプリケーションを探す**
   - 他のDiscordアカウントで確認
   - Railwayの環境変数を確認
   - Application IDで検索

2. **既存のBotが見つかった場合**
   - そのアカウントでログインして設定を確認
   - `applications.commands` スコープを追加
   - Botを再デプロイ

3. **既存のBotが見つからない場合**
   - 新規作成を検討（既存のBotと別物になることを理解）
   - BotのトークンをRailwayの環境変数に設定
   - Botをサーバーに追加（`applications.commands`スコープ付き）
   - Botを再デプロイ
   - コマンドが表示されるか確認

