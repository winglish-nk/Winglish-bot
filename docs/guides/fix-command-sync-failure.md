# 🔧 スラッシュコマンド同期失敗の対処法

## 問題の症状

ログに以下のようなメッセージが表示される場合、スラッシュコマンドの同期が失敗しています：

```
❌ 同期後もコマンドが0個です。同期が失敗しています。
📊 同期後にDiscord APIから取得したコマンド数: 0
📊 同期されたコマンド数（Discord返り値）: 0
```

## 考えられる原因と対処法

### 1. Botに`applications.commands`スコープの権限がない

**症状**: 同期が失敗し、コマンドがDiscordに表示されない

**対処法**:

1. **Discord Developer Portal**を開く: https://discord.com/developers/applications
2. 対象のBotアプリケーションを選択
3. 左サイドバーから **「OAuth2」** → **「URL Generator」** を選択
4. **Scopes**セクションで以下をチェック：
   - ✅ `bot`
   - ✅ `applications.commands` ← **これが重要！**
5. **BOT PERMISSIONS**セクションで必要な権限を選択：
   - ✅ Send Messages
   - ✅ Manage Channels
   - ✅ Read Message History
   - など
6. 生成されたURLをコピー
7. ブラウザでURLを開き、Botをサーバーに**再追加**する

**重要**: Botを再追加する際は、`applications.commands`スコープが含まれていることを確認してください。

---

### 2. Botがギルドに追加されていない、または正しいギルドに追加されていない

**確認方法**:

- Discordでサーバー（ギルド）のメンバーリストを確認
- Botがメンバーとして表示されているか確認

**対処法**:

- Botが表示されていない場合は、上記の手順でBotをサーバーに追加
- 別のサーバーに追加してしまった場合は、正しいサーバーに追加し直す

---

### 3. テストギルドIDが間違っている

**確認方法**:

ログに表示されている`TEST_GUILD_ID`が、実際のDiscordサーバーIDと一致しているか確認

**対処法**:

1. Discordでサーバー名を右クリック → **「サーバー設定」**
2. 左サイドバーの **「ウィジェット」** を選択
3. **「サーバーID」** をコピー
4. Railwayの環境変数`TEST_GUILD_ID`に正しいIDを設定
5. Botを再デプロイ

---

### 4. Application IDが設定されていない

**確認方法**:

ログに以下のように表示されているか確認：

```
📋 Bot Application ID: 1433634632053821593
```

IDが表示されていない場合は、Botのトークンが無効な可能性があります。

**対処法**:

1. Discord Developer PortalでBotのトークンを確認
2. Railwayの環境変数`DISCORD_TOKEN`に正しいトークンを設定
3. Botを再デプロイ

---

## よくある質問

### Q: 同期は成功しているように見えるが、コマンドが表示されない

A: 以下のいずれかが原因の可能性があります：

1. **Discordのキャッシュ**: Discordアプリを再起動してみてください
2. **反映時間**: グローバル同期の場合、最大1時間かかることがあります
3. **権限の問題**: Botに`applications.commands`スコープが付与されていない

### Q: `tree.sync()`の戻り値が空でも、コマンドは動作するか？

A: 既存のコマンドを更新する場合、`tree.sync()`が空のリストを返すことがあります。しかし、同期後に`fetch_commands()`でコマンドが取得できない場合は、同期が失敗している可能性が高いです。

---

## 確認手順

1. **ログを確認**:
   - `📊 同期後にDiscord APIから取得したコマンド数`が0個でないか確認
   - エラーメッセージがないか確認

2. **Discord Developer Portalを確認**:
   - Botに`applications.commands`スコープが付与されているか確認
   - Botが正しいサーバーに追加されているか確認

3. **環境変数を確認**:
   - `DISCORD_TOKEN`が正しく設定されているか
   - `TEST_GUILD_ID`が正しいサーバーIDか

4. **Discordアプリを再起動**:
   - Discordのキャッシュをクリアするため、アプリを再起動

---

## 緊急時の対処法

すべて試しても解決しない場合：

1. Botをサーバーから削除
2. Discord Developer PortalでBotの設定を確認
3. `applications.commands`スコープを含めて、Botを再追加
4. Botを再デプロイ
5. 数分待ってから、Discordでコマンドを確認

