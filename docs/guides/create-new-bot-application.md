# 🆕 新しいBotアプリケーションを作成する手順

このガイドでは、Discord Developer Portalで新しいBotアプリケーションを作成し、Railwayに接続する方法を説明します。

---

## 📋 前提条件

- Discord Developer Portalアカウント（現在ログイン中）
- Railwayアカウント
- Winglish Discordサーバーの管理者権限

---

## 🚀 手順1: 新しいBotアプリケーションを作成

### 1-1. Discord Developer Portalを開く

1. **Discord Developer Portal**にアクセス: https://discord.com/developers/applications
2. **「Applications」**ページに移動（左上の「← Back to Servers」から移動できます）

### 1-2. 新しいアプリケーションを作成

1. **「New Application」**ボタンをクリック
2. **アプリケーション名を入力**: 例「Winglish Bot」または「Winglish Bot (New)」
3. **「Create」**をクリック

### 1-3. Botを追加

1. 左サイドバーから**「Bot」**を選択
2. **「Add Bot」**ボタンをクリック
3. 確認ダイアログで**「Yes, do it!」**をクリック

---

## 🔑 手順2: Botのトークンを取得

### 2-1. トークンを取得

1. **Bot**ページで**「Reset Token」**ボタンをクリック
2. 確認ダイアログで**「Yes, do it!」**をクリック
3. **トークンが表示されたら、すぐにコピー**してください（後で表示できません）
   - トークンの形式: `MTQzMzYzNDYzMjA1MzgyMTU5My5Xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

⚠️ **重要**: トークンは**秘密情報**です。他人に共有しないでください。

---

## ⚙️ 手順3: Botの設定（Intents）

### 3-1. Privileged Gateway Intentsを有効化

**Bot**ページの**「Privileged Gateway Intents」**セクションで、以下を有効化：

- ✅ **MESSAGE CONTENT INTENT** - メッセージの内容を読み取るために必要
- ✅ **SERVER MEMBERS INTENT** - サーバーメンバー情報を取得するために必要
- ✅ **PRESENCE INTENT** - ユーザーのステータスを取得するために必要（オプション）

### 3-2. 設定を保存

- 各設定を有効化すると、自動的に保存されます

---

## 🔐 手順4: OAuth2 URLを生成（Botをサーバーに追加するため）

### 4-1. OAuth2 URL Generatorを開く

1. 左サイドバーから**「OAuth2」**を選択
2. **「URL Generator」**をクリック

### 4-2. Scopesを設定

**「SCOPES」**セクションで以下をチェック：

- ✅ **`bot`** - Botを追加するために必要
- ✅ **`applications.commands`** ← **重要！** スラッシュコマンドを使用するために必須

### 4-3. Bot Permissionsを設定

**「BOT PERMISSIONS」**セクションで、必要な権限をチェック：

- ✅ **Send Messages** - メッセージを送信
- ✅ **Embed Links** - 埋め込みリンクを送信
- ✅ **Attach Files** - ファイルを添付
- ✅ **Read Message History** - メッセージ履歴を読む
- ✅ **Use External Emojis** - 外部絵文字を使用
- ✅ **Manage Channels** - チャンネル管理（個人チャンネル作成に必要）
- ✅ **View Channels** - チャンネルを表示

### 4-4. URLをコピー

1. 設定した権限に基づいて、**「Generated URL」**が自動生成されます
2. **URLをコピー**してください
   - 例: `https://discord.com/api/oauth2/authorize?client_id=1234567890123456789&permissions=8&scope=bot%20applications.commands`

---

## 🤖 手順5: BotをDiscordサーバーに追加

### 5-1. ブラウザでURLを開く

1. コピーしたURLをブラウザのアドレスバーに貼り付けて開く
2. または、URLを直接クリック

### 5-2. サーバーを選択

1. **「サーバーを選択」**ドロップダウンから**「Winglish」**サーバーを選択
2. **「続行」**をクリック

### 5-3. 権限を確認

1. Botに付与される権限が表示されます
2. 問題なければ**「認証」**をクリック

### 5-4. 認証を完了

1. **「I'm not a robot」**チェックボックスにチェック
2. **認証が完了**すると、Botがサーバーに追加されます

---

## ⚙️ 手順6: Railwayの環境変数を更新

### 6-1. Railwayにアクセス

1. **Railway**ダッシュボードにアクセス: https://railway.app
2. **「Winglish-bot」**サービスを選択

### 6-2. 環境変数を更新

1. **「Variables」**タブを選択
2. **「DISCORD_TOKEN」**環境変数を探す
3. **「Edit」**をクリック
4. **新しいBotのトークン**を貼り付け
5. **「Save」**をクリック

⚠️ **注意**: この変更により、既存のBotは動作しなくなります。新しいBotに切り替わります。

---

## 🔄 手順7: Botを再デプロイ

### 7-1. RailwayでBotを再起動

環境変数を更新すると、Railwayが自動的に再デプロイを開始します。

または、手動で再起動する場合：

```bash
cd /tmp/Winglish-bot
railway redeploy --yes
```

### 7-2. ログを確認

1. Railwayの**「Deployments」**タブで、最新のデプロイを確認
2. **「View Logs」**をクリック
3. 以下のログが表示されることを確認：
   - ✅ `✅ Cog 読み込み完了: cogs.notebook`
   - ✅ `✅ スラッシュコマンド同期完了`
   - ✅ `✅ Logged in as Winglish Bot#xxxx (新しいApplication ID)`

---

## ✅ 手順8: 動作確認

### 8-1. Discordでコマンドを確認

1. Discordサーバーで**スラッシュコマンド**を入力
2. `/`を入力して、以下のコマンドが表示されることを確認：
   - `/start`
   - `/notebook_create`
   - `/notebook_list`
   - `/sys_notebooks` ← **これが表示されれば成功！**
   - その他のコマンド

### 8-2. テスト実行

1. `/start`コマンドを実行して、メニューが表示されることを確認
2. `/sys_notebooks`コマンドを実行して、システム推奨単語帳が表示されることを確認

---

## ⚠️ トラブルシューティング

### 問題1: コマンドが表示されない

**原因**: `applications.commands`スコープが含まれていない、または同期が完了していない

**解決方法**:
1. OAuth2 URL Generatorで`applications.commands`スコープが含まれているか確認
2. Botをサーバーから削除して、再度追加（新しいURLを使用）
3. Botの再起動を待つ（最大1時間かかる場合があります）
4. `TEST_GUILD_ID`が設定されている場合、そのサーバーで確認

### 問題2: Botがログインしない

**原因**: トークンが間違っている、またはIntentsが有効化されていない

**解決方法**:
1. Railwayの環境変数`DISCORD_TOKEN`が正しく設定されているか確認
2. Discord Developer PortalでIntentsが有効化されているか確認
3. Railwayのログを確認してエラーメッセージを確認

### 問題3: 既存のBotが動作しなくなった

**原因**: Railwayの環境変数`DISCORD_TOKEN`を変更したため

**解決方法**:
- これは**正常な動作**です。新しいBotに切り替わったため、既存のBotは動作しません
- 既存のBotが必要な場合、元のトークンに戻してください

---

## 📝 チェックリスト

作成手順のチェックリスト：

- [ ] Discord Developer Portalで新しいアプリケーションを作成
- [ ] Botを追加
- [ ] トークンを取得してコピー
- [ ] Intentsを有効化（MESSAGE CONTENT, SERVER MEMBERS）
- [ ] OAuth2 URL Generatorで`bot`と`applications.commands`スコープを設定
- [ ] Bot Permissionsを設定
- [ ] 生成されたURLでBotをサーバーに追加
- [ ] Railwayの環境変数`DISCORD_TOKEN`を更新
- [ ] RailwayでBotを再デプロイ
- [ ] ログでBotの起動を確認
- [ ] Discordでコマンドが表示されることを確認
- [ ] `/sys_notebooks`コマンドが動作することを確認

---

## 🎉 完了

新しいBotアプリケーションの作成が完了しました！

次のステップ：
- Botの動作をテストする
- 既存のBotアプリケーションを削除する（不要な場合）
- コマンドが正しく動作するか確認する

