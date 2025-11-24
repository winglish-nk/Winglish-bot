# システム推奨単語帳のデータソース

> **重要**: システム推奨単語帳は、既存のwordsテーブル（NGSLの3800語）から単語を選んで作る

---

## 🎯 基本的な原則

### データソース

- ✅ **既存のwordsテーブル（NGSLの3800語）のみを使用**
- ❌ 新しい単語データは追加しない
- ❌ 外部データソースは使用しない

### 単語帳の作成方法

1. **既存のwordsテーブルから単語を選ぶ**
2. **levelフィールドや他の条件で分類**
3. **system_notebook_wordsテーブルに記録**

---

## 📊 既存データの構造

### wordsテーブル

```sql
CREATE TABLE words (
    word_id SERIAL PRIMARY KEY,
    word TEXT NOT NULL UNIQUE,
    jp TEXT NOT NULL,
    pos TEXT,
    cefr TEXT,
    level INT,  -- ← これを使って分類
    topic_tags TEXT[],
    synonyms TEXT[],
    antonyms TEXT[],
    derived TEXT[],
    example_en TEXT,
    example_ja TEXT
);
```

**既存データ:**
- NGSLの約3800語が入っている
- `level`フィールドで分類されている（1, 2, 3など）

---

## 📚 システム推奨単語帳の例

### 1. NGSL Level 1

```sql
-- wordsテーブルのlevel=1から全ての単語を選ぶ
INSERT INTO system_notebook_words (notebook_id, word_id, order_index)
SELECT $1, word_id, row_number() OVER (ORDER BY word_id) as order_index
FROM words 
WHERE level = 1 
ORDER BY word_id
```

**説明:**
- wordsテーブルの`level = 1`の単語を全て選ぶ
- 単語数は実際のデータに依存（例: 1000語）

---

### 2. NGSL Level 2

```sql
-- wordsテーブルのlevel=2から全ての単語を選ぶ
INSERT INTO system_notebook_words (notebook_id, word_id, order_index)
SELECT $1, word_id, row_number() OVER (ORDER BY word_id) as order_index
FROM words 
WHERE level = 2 
ORDER BY word_id
```

---

### 3. 「ターゲット1900」（イメージ名）

**注意: 「ターゲット1900」という名前はイメージで、既存のNGSLデータから1900語を選ぶ**

```sql
-- 既存のwordsテーブルから1900語を選ぶ
-- 例: level 1と2を組み合わせて1900語
INSERT INTO system_notebook_words (notebook_id, word_id, order_index)
SELECT $1, word_id, row_number() OVER (ORDER BY level, word_id) as order_index
FROM words 
WHERE level IN (1, 2)  -- または適切な条件
ORDER BY level, word_id
LIMIT 1900
```

**実際の選択方法:**
- level 1と2を組み合わせる
- または、level 1だけで1900語に達する場合はそれを使う
- 実際の単語数は既存データに依存

---

## 🔍 単語の選択基準

### 選択方法の例

#### 方法1: levelで分類

```sql
-- level=1のみ
WHERE level = 1

-- level=1と2
WHERE level IN (1, 2)

-- level=1, 2, 3（全て）
WHERE level IN (1, 2, 3)
```

#### 方法2: 上位N件

```sql
-- level=1の上位1000語
WHERE level = 1 
ORDER BY word_id
LIMIT 1000
```

#### 方法3: 条件を組み合わせ

```sql
-- level=1で、特定のtopic_tagsがある単語
WHERE level = 1 
  AND '大学受験' = ANY(topic_tags)
```

---

## ⚠️ 注意点

### 1. データは既存のwordsテーブルのみ

- ❌ 新しい単語データを追加しない
- ❌ 外部データソース（CSV、API）から取得しない
- ✅ wordsテーブルにある3800語のみを使用

### 2. 単語数は実際のデータに依存

- 「ターゲット1900」という名前はイメージ
- 実際の単語数は既存データに依存（1900語に満たない場合もある）
- 単語帳の説明に「約1900語」などと記載する

### 3. levelフィールドの値

- wordsテーブルの`level`フィールドの値に依存
- データを確認してから作成する
- もしlevelが1, 2, 3でない場合は、適切に条件を調整する

---

## 💻 実装時の確認事項

### 事前確認

```python
async def check_words_data():
    """wordsテーブルのデータを確認"""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # 全体の単語数
        total = await conn.fetchval("SELECT COUNT(*) FROM words")
        print(f"全体の単語数: {total}")
        
        # level別の単語数
        level_counts = await conn.fetch("""
            SELECT level, COUNT(*) as count 
            FROM words 
            GROUP BY level 
            ORDER BY level
        """)
        print("Level別の単語数:")
        for row in level_counts:
            print(f"  Level {row['level']}: {row['count']}語")
        
        # 実際のlevelの値
        levels = await conn.fetch("SELECT DISTINCT level FROM words ORDER BY level")
        print(f"存在するLevel: {[r['level'] for r in levels]}")
```

---

## 📝 まとめ

### システム推奨単語帳の作成

1. ✅ **既存のwordsテーブル（NGSLの3800語）から単語を選ぶ**
2. ✅ **levelフィールドや他の条件で分類**
3. ✅ **system_notebook_wordsテーブルに記録**

### 重要なポイント

- 「ターゲット1900」という名前は**イメージ**で、実際には既存データから選ぶ
- 新しい単語データは追加しない
- 単語数は実際のデータに依存する

---

**結論**: システム推奨単語帳は、既存のNGSLデータを効率的に活用するための機能。新しいデータを追加する必要はない。
