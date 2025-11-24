# RailwayでGitHubリポジトリを接続する方法

> Winglish-botサービスにGitHubリポジトリを正しく接続する手順

---

## 🎯 目的

既存の「Winglish-bot」サービスに、GitHubリポジトリ（`winglish-nk/Winglish-bot`）を接続して、自動デプロイを設定します。

---

## ✅ 正しい手順

### ステップ1: 既存のWinglish-botサービスを選択

1. Railwayダッシュボードで、左側のサービスリストから「**Winglish-bot**」をクリック
2. 「**Settings**」タブを開く

---

### ステップ2: GitHubリポジトリを接続

1. Settingsタブの「**Source**」セクションを見つける
2. 「**Connect Repo**」ボタンをクリック
3. 表示されるリストから「**winglish-nk/Winglish-bot**」を選択
4. ブランチを「**main**」に設定

---

### ステップ3: 環境変数を確認

GitHubリポジトリを接続すると、環境変数がリセットされる可能性があります。

「**Variables**」タブを開いて、以下の環境変数が設定されているか確認：

- `DISCORD_TOKEN`
- `DATABASE_PUBLIC_URL` または `DATABASE_URL`
- `DIFY_API_KEY_QUESTION`（必要に応じて）
- `DIFY_API_KEY_ANSWER`（必要に応じて）
- その他の必要な環境変数

**環境変数が設定されていない場合は、設定してください。**

---

### ステップ4: デプロイを確認

リポジトリを接続すると、自動的にデプロイが開始されます。

1. 「**Deployments**」タブを開く
2. 新しいデプロイが「**Building**」や「**Deploying**」になっているか確認
3. デプロイが完了するまで待つ（「**Active**」になるまで）

---

### ステップ5: ログを確認

デプロイが完了したら、「**Logs**」タブで以下のログが表示されるか確認：

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

## 🗑️ 間違って作ったサービスを削除する（オプション）

もし「discerning-abundance」などの新しいサービスを作ってしまった場合：

1. 左側のサービスリストで、そのサービスをクリック
2. 「**Settings**」タブを開く
3. 下の方までスクロール
4. 「**Danger Zone**」セクションを見つける
5. 「**Delete Service**」ボタンをクリック

**注意**: 削除する前に、必要なデータがないか確認してください。

---

## 🔍 確認チェックリスト

- [ ] 既存の「Winglish-bot」サービスを選択している
- [ ] 「Settings」タブの「Source」セクションで「Connect Repo」をクリックした
- [ ] 「winglish-nk/Winglish-bot」リポジトリを選択した
- [ ] ブランチを「main」に設定した
- [ ] 環境変数が正しく設定されているか確認した
- [ ] デプロイが開始されているか確認した
- [ ] デプロイ完了後のログを確認した
- [ ] 「✅ Cog 読み込み完了: cogs.notebook」が表示されている

---

## 💡 まとめ

1. **既存のWinglish-botサービス**にGitHubリポジトリを接続
2. **環境変数**を確認・設定
3. **デプロイ**が自動的に開始される
4. **ログ**で正常に起動しているか確認

これで、新しいコード（notebook Cog）がデプロイされ、`/notebook_*`コマンドが使えるようになるはずです！
