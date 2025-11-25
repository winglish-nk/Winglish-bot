# 🔧 新しいBot作成後のスラッシュコマンド同期失敗の対処法

## 問題: 新しいBotを作成したが、スラッシュコマンドが表示されない

ログに以下のエラーが表示される場合：
```
❌ 同期後もコマンドが0個です。同期が失敗しています。
❌ 考えられる原因:
   1. Botに'applications.commands'スコープの権限がない
   2. Botがギルドに追加されていない
   3. Application IDが設定されていない
```

---

## ✅ 解決方法: `applications.commands`スコープを追加

新しいBotを作成した際に、**`applications.commands`スコープが含まれていない**可能性が高いです。

### 手順1: OAuth2 URL Generatorを確認

1. **Discord Developer Portal**を開く: https://discord.com/developers/applications
2. 新しいBotアプリケーション（Application ID: `1442793864216969268`）を選択
3. 左サイドバーから**「OAuth2」** → **「URL Generator」**を選択

### 手順2: Scopesを確認・修正

**「SCOPES」**セクションで、以下が**両方とも**チェックされているか確認：

- ✅ **`bot`** - Botを追加するために必要
- ✅ **`applications.commands`** ← **重要！これが必須**

もし`applications.commands`がチェックされていなければ：
1. **`applications.commands`**をチェック
2. **新しいURLが自動生成**されます
3. **新しいURLをコピー**してください

### 手順3: Botをサーバーから削除

1. **Discord**で**「Winglish」**サーバーを開く
2. サーバー名を右クリック
3. **「サーバー設定」**を選択
4. 左サイドバーから**「メンバー」**を選択
5. **「Winglish Bot」（または新しいBot名）**を探す
6. Botの名前をクリック
7. **「サーバーから削除」**をクリック
8. 確認ダイアログで**「削除」**をクリック

### 手順4: Botを再追加（`applications.commands`スコープ付き）

1. **手順2でコピーした新しいURL**をブラウザで開く
2. **「サーバーを選択」**ドロップダウンから**「Winglish」**サーバーを選択
3. **「続行」**をクリック
4. Botに付与される権限を確認（`applications.commands`が含まれているはず）
5. **「認証」**をクリック
6. **「I'm not a robot」**チェックボックスにチェック
7. 認証を完了

### 手順5: Botを再起動

#### 方法1: Railwayで再デプロイ

1. **Railway**ダッシュボードにアクセス: https://railway.app
2. **「Winglish-bot」**サービスを選択
3. **「Deployments」**タブを選択
4. 最新のデプロイの**「...」**メニューをクリック
5. **「Redeploy」**をクリック

#### 方法2: Railway CLIで再デプロイ

```bash
cd /tmp/Winglish-bot
railway redeploy --yes
```

#### 方法3: 空のコミットをプッシュ

```bash
cd /tmp/Winglish-bot
git commit --allow-empty -m "Trigger redeploy to sync slash commands"
git push origin main
```

### 手順6: ログを確認

1. Railwayの**「Deployments」**タブで、最新のデプロイを確認
2. **「View Logs」**をクリック
3. 以下のログが表示されることを確認：
   - ✅ `✅ スラッシュコマンド同期完了`
   - ✅ `📊 同期されたコマンド数（Discord返り値）: 9`（または9個以上）
   - ✅ `📊 同期後にDiscord APIから取得したコマンド数: 9`（または9個以上）

### 手順7: Discordでコマンドを確認

1. Discordサーバーで**スラッシュコマンド**を入力
2. `/`を入力して、以下のコマンドが表示されることを確認：
   - `/start`
   - `/notebook_create`
   - `/notebook_list`
   - `/sys_notebooks` ← **これが表示されれば成功！**
   - その他のコマンド

---

## ⚠️ 注意事項

### 時間がかかる場合

- Botをサーバーに追加してから、スラッシュコマンドが表示されるまでに**最大1時間**かかる場合があります
- `TEST_GUILD_ID`が設定されている場合、テストギルドでは**すぐに反映**されます

### グローバル同期の場合

- `TEST_GUILD_ID`が設定されていない場合、コマンドは**グローバル同期**されます
- グローバル同期は**最大1時間**かかります

### テストギルドで即座に確認したい場合

- Railwayの環境変数`TEST_GUILD_ID`を設定
- テストギルドのIDを設定すると、そのギルドでは即座にコマンドが表示されます

---

## 🔍 トラブルシューティング

### 問題1: まだコマンドが表示されない

**確認事項**:

1. **Botがサーバーに追加されているか確認**
   - Discord > サーバー設定 > メンバー でBotが表示されているか確認

2. **OAuth2 URLに`applications.commands`が含まれているか確認**
   - URLに`scope=bot%20applications.commands`が含まれているか確認
   - 例: `https://discord.com/api/oauth2/authorize?client_id=...&scope=bot%20applications.commands&...`

3. **Botの再起動を待つ**
   - 最大1時間待ってから再度確認

4. **ログで同期エラーを確認**
   - Railwayのログで、`tree.sync()`のエラーがないか確認

### 問題2: `tree.sync()`でエラーが発生する

ログに以下のエラーが表示される場合：

```
discord.app_commands.CommandSyncFailure
discord.Forbidden: 403 Forbidden
```

**解決方法**:

1. **Botに`applications.commands`スコープが付与されているか確認**
2. **Botがギルドに追加されているか確認**
3. **Botに適切な権限があるか確認**

---

## 📋 チェックリスト

- [ ] OAuth2 URL Generatorで`bot`と`applications.commands`スコープがチェックされている
- [ ] 新しいURL（`applications.commands`スコープ付き）をコピーした
- [ ] 既存のBotをサーバーから削除した
- [ ] 新しいURLでBotをサーバーに再追加した
- [ ] Botを再起動（再デプロイ）した
- [ ] ログで同期が成功していることを確認した
- [ ] Discordでコマンドが表示されることを確認した

---

## 🎉 成功の確認

以下の条件が満たされれば成功です：

- ✅ ログに`📊 同期されたコマンド数（Discord返り値）: 9`以上が表示される
- ✅ ログに`📊 同期後にDiscord APIから取得したコマンド数: 9`以上が表示される
- ✅ Discordで`/sys_notebooks`コマンドが表示される
- ✅ `/start`コマンドを実行して、メニューが表示される

---

## 📝 次のステップ

スラッシュコマンドが表示されたら：

1. `/start`コマンドを実行して、メニューが表示されることを確認
2. `/sys_notebooks`コマンドを実行して、システム推奨単語帳が表示されることを確認
3. その他のコマンドをテスト

