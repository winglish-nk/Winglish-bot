# システム推奨単語帳の作成方法

システム推奨単語帳（「大学受験必須単語」「NGSL Level 1, 2, 3」など）を作成する方法を説明します。

---

## 📋 概要

システム推奨単語帳は、既存のNGSLデータ（wordsテーブル）から自動的に作成されます。

### 作成される単語帳

1. **中学英単語 Level 1** - wordsテーブルの`level=1`の単語（中学英単語）
2. **中学英単語 Level 2** - wordsテーブルの`level=2`の単語（中学英単語）
3. **高校単語・入試必須 Level 3-10** - wordsテーブルの`level=3-10`の単語（各レベルごとに単語帳を作成）
4. **大学受験必須単語** - level 3以上全ての単語（高校単語・入試必須から選択）

**注意**: Level 3-10は、データベースに存在するレベルごとに自動的に単語帳が作成されます。

---

## 🚀 実行方法

### 1. 環境変数の確認

`.env`ファイルに`DATABASE_PUBLIC_URL`または`DATABASE_URL`が設定されていることを確認してください。

```bash
# .envファイルを確認
cat .env | grep DATABASE
```

### 2. スクリプトの実行

#### 方法A: Railway CLIを使用（推奨）

Railway CLIをインストールしていない場合:
```bash
# Railway CLIをインストール（Mac）
brew install railway

# または npm経由
npm i -g @railway/cli
```

Railway CLIで実行:
```bash
# Railwayにログイン
railway login

# プロジェクトを選択
railway link

# スクリプトを実行（Railwayの環境変数が自動的に使用されます）
railway run python scripts/create_system_notebooks.py
```

#### 方法B: ローカルで実行

```bash
# 環境変数を設定して実行
export DATABASE_PUBLIC_URL="your_database_url"
python3 scripts/create_system_notebooks.py
```

または、`.env`ファイルを作成:
```bash
# .envファイルを作成
echo "DATABASE_PUBLIC_URL=your_database_url" > .env

# 実行
python3 scripts/create_system_notebooks.py
```

### 3. 実行結果の確認

スクリプトを実行すると、以下の情報が表示されます:

```
📊 wordsテーブルのデータを確認中...
  全体の単語数: 3800語
  Level別の単語数:
    Level 1: 1000語
    Level 2: 900語
    Level 3: 800語
  存在するLevel: [1, 2, 3]

🚀 システム推奨単語帳を作成します...

📚 システム推奨単語帳を作成中...

1. 中学英単語 Level 1を作成中...
   ✅ 中学英単語 Level 1を作成しました（1000語）
2. 中学英単語 Level 2を作成中...
   ✅ 中学英単語 Level 2を作成しました（900語）
3. 高校単語・入試必須 Level 3-10を作成中...
   ✅ 高校単語・入試必須 Level 3を作成しました（800語）
   ✅ 高校単語・入試必須 Level 4を作成しました（700語）
   ✅ 高校単語・入試必須 Level 5を作成しました（600語）
   ... (Level 10まで続く)
4. 大学受験必須単語を作成中（level 3-10から選択）...
   ✅ 大学受験必須単語を作成しました（5000語）

✅ システム推奨単語帳の作成が完了しました！
```

---

## ⚠️ 既存のシステム推奨単語帳がある場合

既存のシステム推奨単語帳が存在する場合、以下のように確認が求められます:

```
⚠️ 既存のシステム推奨単語帳が12個見つかりました:
  - 中学英単語 Level 1 (ngsl_level1)
  - 中学英単語 Level 2 (ngsl_level2)
  - 高校単語・入試必須 Level 3 (ngsl_level3)
  - 高校単語・入試必須 Level 4 (ngsl_level4)
  ... (Level 10まで続く)
  - 大学受験必須単語 (entrance_exam_essential)

既存のシステム推奨単語帳を削除して再作成しますか？ (y/N):
```

`y`を入力すると、既存のシステム推奨単語帳が削除され、新しく作成されます。

---

## 📊 データベースへの保存

システム推奨単語帳は以下のテーブルに保存されます:

### `vocabulary_notebooks`テーブル

- `user_id`: `NULL`（システム推奨のため）
- `is_system`: `TRUE`
- `system_type`: `'ngsl_level1'`, `'ngsl_level2'`, `'ngsl_level3'`, `'ngsl_level4plus'`, `'entrance_exam_essential'`など

### `system_notebook_words`テーブル

- `notebook_id`: 単語帳ID
- `word_id`: 単語ID（wordsテーブルから）
- `order_index`: 学習順序

---

## 🔍 確認方法

### Discordで確認

1. `/notebook_list_system`コマンドを実行
2. システム推奨単語帳の一覧が表示されます

### データベースで確認

```sql
-- システム推奨単語帳一覧
SELECT notebook_id, name, description, system_type 
FROM vocabulary_notebooks 
WHERE is_system = TRUE;

-- 各単語帳の単語数
SELECT n.name, COUNT(snw.word_id) as word_count
FROM vocabulary_notebooks n
LEFT JOIN system_notebook_words snw ON n.notebook_id = snw.notebook_id
WHERE n.is_system = TRUE
GROUP BY n.notebook_id, n.name;
```

---

## 📝 注意事項

1. **既存データのみ使用**: 新しい単語データは追加されません。既存のwordsテーブル（NGSLの約3800語）から選びます。

2. **単語の分類**:
   - **Level 1, 2**: 中学英単語
   - **Level 3以上**: 高校単語・入試必須

3. **単語数はデータ依存**: 実際の単語数は既存データに依存します。大学受験必須単語はlevel 3以上（高校単語・入試必須）の全単語を含みます。

4. **levelフィールド**: wordsテーブルの`level`フィールドに値が設定されている必要があります。

4. **再実行**: 同じスクリプトを再実行すると、既存のシステム推奨単語帳を削除してから新しく作成されます。

---

## 🐛 トラブルシューティング

### エラー: "wordsテーブルにデータがありません"

→ まず`scripts/load_words.py`を実行してwordsテーブルにデータを投入してください。

### エラー: "Level別のデータが見つかりませんでした"

→ wordsテーブルの`level`フィールドに値が設定されていない可能性があります。CSVファイルを確認してください。

### エラー: "既存のシステム推奨単語帳が削除できません"

→ データベース接続や権限を確認してください。

---

**関連ドキュメント**: [system-notebooks-data-source.md](system-notebooks-data-source.md)

