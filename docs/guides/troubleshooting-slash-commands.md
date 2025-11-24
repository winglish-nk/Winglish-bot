# スラッシュコマンドが表示されない場合の対処法

> 新しいスラッシュコマンド（`/notebook_*`など）がDiscordに表示されない場合の解決方法

---

## 🔍 問題: スラッシュコマンドが表示されない

### 症状
- `/notebook_create`、`/notebook_list`などのコマンドが表示されない
- `/`を入力してもコマンド候補に出てこない

### 原因
スラッシュコマンドは、Bot起動時にDiscord APIに同期する必要があります。新しいコマンドを追加した後は、Botを再起動する必要があります。

---

## ✅ 解決方法

### 方法1: Botを再起動（推奨）

1. **Railwayの場合**
   - RailwayダッシュボードでBotサービスを確認
   - 「Restart」ボタンをクリックして再起動
   - または、新しいコードをプッシュしてデプロイ

2. **ローカル開発の場合**
   - Botを停止（Ctrl+C）
   - 再度起動: `python main.py`

3. **再起動後の確認**
   - Botのログで以下のメッセージを確認:
     ```
     ✅ Cog 読み込み完了: cogs.notebook
     ✅ スラッシュコマンド同期完了（グローバル）
     ```
   - Discordで `/` を入力してコマンドが表示されるか確認

---

### 方法2: スラッシュコマンドを強制同期

スラッシュコマンドを強制的に同期するスクリプトを実行:

```python
# scripts/sync_commands.py
import asyncio
import discord
from config import DISCORD_TOKEN, TEST_GUILD_ID

async def sync_commands():
    bot = discord.Client(intents=discord.Intents.default())
    
    @bot.event
    async def on_ready():
        print(f'✅ Logged in as {bot.user}')
        
        # スラッシュコマンドツリーを取得
        tree = discord.app_commands.CommandTree(bot)
        
        # Cogからコマンドを読み込む
        await bot.load_extension('cogs.notebook')
        # 他のCogも必要に応じて読み込む
        
        try:
            if TEST_GUILD_ID:
                guild = discord.Object(id=int(TEST_GUILD_ID))
                tree.copy_global_to(guild=guild)
                await tree.sync(guild=guild)
                print(f'✅ スラッシュコマンド同期完了（テストギルド: {TEST_GUILD_ID}）')
            else:
                await tree.sync()
                print('✅ スラッシュコマンド同期完了（グローバル）')
        except Exception as e:
            print(f'❌ 同期失敗: {e}')
        
        await bot.close()
    
    await bot.start(DISCORD_TOKEN)

asyncio.run(sync_commands())
```

---

### 方法3: テストギルドIDを使う（開発時）

**グローバル同期は最大1時間かかることがあります**。

開発中は、`TEST_GUILD_ID`を設定すると、即座に反映されます：

1. `.env`ファイルに追加:
   ```
   TEST_GUILD_ID=あなたのDiscordサーバーID
   ```

2. DiscordサーバーIDの取得方法:
   - Discord設定 → 詳細設定 → 開発者モードをON
   - サーバー名を右クリック → 「IDをコピー」

3. Botを再起動

これで、指定したサーバー内ではすぐにコマンドが表示されます。

---

## 📋 確認チェックリスト

- [ ] Botが再起動されている
- [ ] ログに「✅ Cog 読み込み完了: cogs.notebook」が表示されている
- [ ] ログに「✅ スラッシュコマンド同期完了」が表示されている
- [ ] Discordで `/` を入力してコマンドが表示される
- [ ] エラーログがないか確認

---

## 🔍 トラブルシューティング

### 問題1: Cogが読み込まれていない

**ログに「❌ Cog 読み込み失敗: cogs.notebook」が表示される**

**確認事項:**
- `cogs/notebook.py` ファイルが存在する
- ファイルに構文エラーがない
- インポートエラーがない

**解決方法:**
```bash
# 構文チェック
python -m py_compile cogs/notebook.py

# エラーがあれば修正
```

---

### 問題2: スラッシュコマンド同期が失敗している

**ログに「❌ スラッシュコマンド同期失敗」が表示される**

**原因:**
- Discord APIのレート制限
- 権限不足
- ネットワークエラー

**解決方法:**
1. 数分待ってから再試行
2. Botに必要な権限があるか確認
3. ログの詳細なエラーメッセージを確認

---

### 問題3: コマンドが一部のサーバーにしか表示されない

**原因:**
- `TEST_GUILD_ID`が設定されている場合、指定したサーバーにのみ同期される

**解決方法:**
- グローバル同期にする場合: `.env`から`TEST_GUILD_ID`を削除
- Botを再起動

---

## 💡 ベストプラクティス

### 開発時
1. ✅ `TEST_GUILD_ID`を設定して即座に反映
2. ✅ 新しいコマンドを追加したら必ずBotを再起動
3. ✅ ログを確認して同期が成功しているかチェック

### 本番環境
1. ✅ `TEST_GUILD_ID`は削除（グローバル同期）
2. ✅ 新しいコマンドを追加したらBotを再起動
3. ✅ 最大1時間待つ（グローバル同期は時間がかかる）

---

## 🎯 今すぐ試す

1. **Botを再起動**
   - Railwayの場合は「Restart」
   - ローカルの場合はCtrl+Cして再起動

2. **ログを確認**
   - `✅ Cog 読み込み完了: cogs.notebook` が表示されるか
   - `✅ スラッシュコマンド同期完了` が表示されるか

3. **Discordで確認**
   - `/` を入力
   - `notebook` で検索
   - `/notebook_create`、`/notebook_list`などが表示されるか確認

---

**結論**: 新しいスラッシュコマンドを追加した後は、**必ずBotを再起動**してください。グローバル同期の場合、最大1時間かかることがありますが、通常は数分で反映されます。
