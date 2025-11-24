# RailwayでBotを再起動する方法

> Restartボタンがない場合の再起動方法

---

## 🔄 Botを再起動する方法

RailwayのUIが変わっている場合、Restartボタンが見つからないことがあります。以下の方法で再起動できます。

---

### 方法1: 空のコミットで再デプロイ（推奨）

新しいコードをプッシュすると、Railwayが自動的に再デプロイします。  
既にコードはプッシュ済みなので、**空のコミット**を作成してプッシュすると再デプロイされます。

```bash
cd /tmp/Winglish-bot
git commit --allow-empty -m "Botを再起動するための空コミット"
git push origin main
```

これで、Railwayが自動的に新しいデプロイを開始し、Botが再起動されます。

---

### 方法2: Deploymentsタブから再デプロイ

1. RailwayダッシュボードでBotサービスを開く
2. **「Deployments」タブ**を開く
3. 最新のデプロイの右側にある「**3つの点（...）メニュー**」をクリック
4. 「**Redeploy**」を選択

これで、同じコミットを再デプロイできます。

---

### 方法3: Settingsタブを詳しく見る

Restartボタンが見つからない場合、以下の場所を確認してください：

1. **「Settings」タブ**を開く
2. 下の方までスクロール
3. 「**Danger Zone**」セクションがある場合、そこにRestartボタンがある可能性があります
4. または、「**Service Settings**」の中にRestartボタンがある可能性があります

---

### 方法4: 環境変数を少し変更して保存

1. **「Variables」タブ**を開く
2. 任意の環境変数（例: `LOG_LEVEL`）を開く
3. 値を変更（例: `INFO` → `INFO`）して保存
4. これで再デプロイがトリガーされる場合があります

---

## ✅ 再デプロイの確認方法

再デプロイが開始されると、以下が確認できます：

1. **「Deployments」タブ**で新しいデプロイが表示される
2. デプロイのステータスが「**Building**」や「**Deploying**」になる
3. デプロイが完了すると「**Active**」になる

---

## 📊 再デプロイ後のログ確認

再デプロイが完了したら、以下のログが表示されるはずです：

```
✅ データベース初期化完了
✅ Cog 読み込み完了: cogs.onboarding
✅ Cog 読み込み完了: cogs.menu
✅ Cog 読み込み完了: cogs.vocab
✅ Cog 読み込み完了: cogs.notebook  ← これが重要！
✅ Cog 読み込み完了: cogs.svocm
✅ Cog 読み込み完了: cogs.reading
✅ Cog 読み込み完了: cogs.admin
✅ 永続 View 登録完了
✅ スラッシュコマンド同期完了（グローバル）
✅ Logged in as Winglish#1234
```

---

## 🎯 今すぐ試す（最も簡単な方法）

**空のコミットを作成してプッシュ**するのが最も簡単です：

```bash
cd /tmp/Winglish-bot
git commit --allow-empty -m "Botを再起動"
git push origin main
```

これで、Railwayが自動的に再デプロイし、Botが再起動されます。

---

## 💡 まとめ

Restartボタンが見つからない場合は：
1. **空のコミットを作成してプッシュ**（推奨）
2. **DeploymentsタブからRedeploy**
3. **Settingsタブを詳しく確認**

最も簡単なのは、**空のコミットをプッシュ**する方法です！
