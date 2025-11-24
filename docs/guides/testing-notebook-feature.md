# 単語帳機能のテスト手順

> Phase 1で実装した基本的な単語帳機能のテスト方法

---

## 🧪 テスト前の準備

### 1. データベーススキーマの確認

データベースに新しいテーブルが作成されているか確認します。

**Railwayの場合:**
1. Railwayのダッシュボードでデータベースに接続
2. 以下のSQLを実行してテーブルが存在するか確認

```sql
-- テーブルの存在確認
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('vocabulary_notebooks', 'notebook_words');

-- テーブル構造の確認
\d vocabulary_notebooks
\d notebook_words
```

**ローカル開発環境の場合:**
- `sql/schema.sql` が自動実行されるはずですが、手動で実行する場合:

```bash
psql $DATABASE_URL -f sql/schema.sql
```

---

## 📋 テスト手順

### テスト1: 単語帳の作成

```
/notebook_create name:"テスト単語帳" description:"テスト用の単語帳です"
```

**期待される結果:**
- ✅ 「✅ 単語帳「テスト単語帳」を作成しました！」と表示される
- ❌ 同名の単語帳を作成しようとすると「既に存在します」とエラー

---

### テスト2: 単語帳一覧の表示

```
/notebook_list
```

**期待される結果:**
- ✅ 作成した単語帳が一覧表示される
- ✅ 単語数が「0語」と表示される
- ✅ 説明が表示される

---

### テスト3: 単語を追加

まず、データベースに単語があることを確認:

```sql
SELECT word, jp FROM words LIMIT 5;
```

それから、単語を追加:

```
/notebook_add notebook_name:"テスト単語帳" word:abandon
```

**期待される結果:**
- ✅ 「✅ 単語「abandon (捨てる)」を「テスト単語帳」に追加しました！」と表示
- ❌ 存在しない単語を追加しようとすると「見つかりません」とエラー
- ❌ 同じ単語を2回追加しようとすると「既に追加されています」と表示

---

### テスト4: 単語帳一覧の再確認

```
/notebook_list
```

**期待される結果:**
- ✅ 「テスト単語帳」の単語数が「1語」になっている

---

### テスト5: 単語帳から学習

```
/notebook_study notebook_name:"テスト単語帳"
```

**期待される結果:**
- ✅ 単語帳から10問（実際には1語しかないので1問）が出題される
- ✅ 既存の学習機能（VocabSessionView）と同じUIが表示される
- ✅ 問題に回答できる

---

### テスト6: 複数の単語を追加

```
/notebook_add notebook_name:"テスト単語帳" word:ability
/notebook_add notebook_name:"テスト単語帳" word:able
/notebook_add notebook_name:"テスト単語帳" word:about
```

**期待される結果:**
- ✅ 各単語が正常に追加される
- ✅ `/notebook_list` で単語数が増えている

---

### テスト7: 単語を削除

```
/notebook_remove notebook_name:"テスト単語帳" word:about
```

**期待される結果:**
- ✅ 「✅ 単語「about」を「テスト単語帳」から削除しました。」と表示
- ✅ `/notebook_list` で単語数が減っている

---

### テスト8: 単語帳を削除

```
/notebook_delete name:"テスト単語帳"
```

**期待される結果:**
- ✅ 「✅ 単語帳「テスト単語帳」を削除しました。」と表示
- ✅ `/notebook_list` で単語帳が表示されなくなる
- ✅ 単語帳に含まれていた単語も削除される（CASCADE）

---

## 🔍 エラーテスト

### エラーケース1: 存在しない単語帳を指定

```
/notebook_add notebook_name:"存在しない単語帳" word:abandon
```

**期待される結果:**
- ❌ 「❌ 単語帳「存在しない単語帳」が見つかりません。」とエラー

---

### エラーケース2: 存在しない単語を追加

```
/notebook_add notebook_name:"テスト単語帳" word:xyz123
```

**期待される結果:**
- ❌ 「❌ 単語「xyz123」が見つかりません。」とエラー

---

### エラーケース3: 空の単語帳から学習

単語が0語の単語帳から学習しようとする

```
/notebook_study notebook_name:"空の単語帳"
```

**期待される結果:**
- ❌ 「❌ 単語帳「空の単語帳」に単語がありません。」とエラー

---

## 🗄️ データベース確認

### 単語帳の確認

```sql
-- 単語帳一覧
SELECT notebook_id, user_id, name, description, created_at 
FROM vocabulary_notebooks 
ORDER BY created_at DESC;

-- 単語帳に含まれる単語
SELECT 
    n.name as notebook_name,
    w.word,
    w.jp,
    nw.added_at
FROM notebook_words nw
JOIN vocabulary_notebooks n ON nw.notebook_id = n.notebook_id
JOIN words w ON nw.word_id = w.word_id
WHERE n.user_id = 'YOUR_USER_ID'
ORDER BY n.name, nw.added_at;
```

---

## 📊 正常動作の確認ポイント

### 1. 基本操作が全て動作する
- ✅ 作成、一覧、追加、削除、学習が全て正常に動作

### 2. エラーハンドリングが適切
- ✅ 存在しない単語帳・単語を指定した時に適切なエラーメッセージ
- ✅ 重複追加を防げる

### 3. データベース整合性
- ✅ 単語帳を削除すると、含まれる単語も削除される（CASCADE）
- ✅ ユーザーごとに単語帳が分離されている

### 4. UI/UX
- ✅ メッセージが分かりやすい
- ✅ Embedで見やすく表示される
- ✅ 学習機能が既存のものと同じUIで動作する

---

## 🐛 トラブルシューティング

### 問題1: コマンドが表示されない

**原因:** Cogが読み込まれていない可能性

**確認:**
- Botのログで `✅ Cog 読み込み完了: cogs.notebook` が表示されているか
- `/notebook_list` などのコマンドがスラッシュコマンド一覧に表示されるか

**解決:**
```bash
# Botを再起動
# Railwayの場合はデプロイし直す
```

---

### 問題2: テーブルが存在しない

**原因:** スキーマが適用されていない

**解決:**
```bash
# スキーマを手動で適用
psql $DATABASE_URL -f sql/schema.sql
```

---

### 問題3: 単語が見つからない

**原因:** wordsテーブルにデータがない

**確認:**
```sql
SELECT COUNT(*) FROM words;
```

**解決:**
- NGSLの3800語がインポートされているか確認
- `scripts/load_words.py` でデータを読み込む

---

### 問題4: 学習機能が動作しない

**原因:** VocabSessionViewが正しくインポートされていない

**確認:**
- `cogs/notebook.py` のインポート文を確認
- エラーログを確認

---

## ✅ テスト完了チェックリスト

- [ ] 単語帳の作成ができる
- [ ] 単語帳の一覧が表示できる
- [ ] 単語を追加できる
- [ ] 単語を削除できる
- [ ] 単語帳から学習できる
- [ ] 単語帳を削除できる
- [ ] エラーハンドリングが適切に動作する
- [ ] データベース整合性が保たれている
- [ ] UI/UXが分かりやすい

---

**テストが完了したら、Phase 2（システム推奨単語帳）に進みましょう！**
