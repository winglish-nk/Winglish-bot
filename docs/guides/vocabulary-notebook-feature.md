# 単語帳機能の設計

> Discord上でユーザーが自分の「単語帳」を作成し、管理・学習できる機能

---

## 🎯 機能概要

### ユーザーができること

1. **単語帳の作成・管理**
   - 自分の単語帳を作成（例: 「今週覚える単語」「苦手単語」）
   - 単語を追加・削除
   - 単語帳の一覧表示

2. **単語帳から学習**
   - 作成した単語帳から問題を出題
   - 既存の学習機能（SRS）と連携

3. **自動的な単語帳**
   - 「苦手単語帳」（間違えた単語を自動で追加）
   - 「復習用単語帳」（復習が必要な単語）

---

## 💡 機能詳細

### 1. カスタム単語帳

#### コマンド例
```
/単語帳 作成 "今週覚える単語"
→ 新しい単語帳を作成

/単語帳 追加 "今週覚える単語" "abandon"
→ 単語帳に単語を追加

/単語帳 削除 "今週覚える単語" "abandon"
→ 単語帳から単語を削除

/単語帳 一覧
→ 自分の単語帳一覧を表示

/単語帳 学習 "今週覚える単語"
→ その単語帳から10問出題
```

#### データベース設計
```sql
-- 単語帳テーブル
CREATE TABLE vocabulary_notebooks (
    notebook_id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- 単語帳-単語の関連テーブル
CREATE TABLE notebook_words (
    notebook_id INT REFERENCES vocabulary_notebooks(notebook_id) ON DELETE CASCADE,
    word_id INT REFERENCES words(word_id) ON DELETE CASCADE,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY(notebook_id, word_id)
);
```

---

### 2. 自動的な単語帳

#### 「苦手単語帳」
- 間違えた単語を自動で追加
- ユーザーが「苦手単語帳」を作成すると自動で更新
- 削除は手動

#### 「復習用単語帳」
- SRSの復習が必要な単語を自動で集約
- 次回復習日が近い単語を追加
- 自動更新

---

### 3. 単語帳からの学習

#### 学習フロー
```
1. ユーザーが「/単語帳 学習 "今週覚える単語"」を実行
2. その単語帳の単語から10問（または指定数）を選択
3. 既存の学習機能（vocab.py）を使用
4. 学習結果を記録
```

#### 既存機能との統合
- `VocabMenuView` に「単語帳から学習」ボタンを追加
- 既存の学習フローを再利用

---

## 🎨 UI/UX設計

### 単語帳一覧表示

```
📚 あなたの単語帳

1. 📖 今週覚える単語 (15語)
   作成日: 2025-11-20
   [学習する] [編集] [削除]

2. 📖 苦手単語帳 (23語)
   (自動更新)
   [学習する] [編集]

3. 📖 復習用単語帳 (8語)
   (自動更新)
   [学習する]
```

### 単語帳作成モーダル

```
単語帳名: [入力欄]
説明: [入力欄（オプション）]

[作成] [キャンセル]
```

### 単語追加

```
単語帳: 今週覚える単語

追加する単語を入力してください
[単語入力欄]

または、選択肢から選ぶ:
- abandon
- ability
- able
...
```

---

## 🔄 学習フローとの統合

### 現在のメニュー

```
[英単語] [英文解釈] [長文読解]
```

### 改善後

```
[英単語]
├─ 10問テスト
├─ 前々回テスト
├─ 苦手テスト
└─ 単語帳から学習
    ├─ 今週覚える単語
    ├─ 苦手単語帳
    └─ [単語帳一覧]
```

---

## 💻 実装方法

### 1. データベーススキーマ追加

```sql
-- sql/schema.sql に追加

-- 単語帳テーブル
CREATE TABLE IF NOT EXISTS vocabulary_notebooks (
    notebook_id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    is_auto BOOLEAN DEFAULT FALSE,  -- 自動更新かどうか
    auto_type TEXT,  -- 'weak', 'review', etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- 単語帳-単語の関連テーブル
CREATE TABLE IF NOT EXISTS notebook_words (
    notebook_id INT NOT NULL REFERENCES vocabulary_notebooks(notebook_id) ON DELETE CASCADE,
    word_id INT NOT NULL REFERENCES words(word_id) ON DELETE CASCADE,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY(notebook_id, word_id)
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_notebook_words_notebook ON notebook_words(notebook_id);
CREATE INDEX IF NOT EXISTS idx_notebook_words_word ON notebook_words(word_id);
CREATE INDEX IF NOT EXISTS idx_vocabulary_notebooks_user ON vocabulary_notebooks(user_id);
```

---

### 2. スラッシュコマンド実装

```python
# cogs/vocab.py または新しい cogs/notebook.py に追加

@discord.app_commands.command(name="notebook_create", description="新しい単語帳を作成")
async def notebook_create(self, interaction: discord.Interaction, name: str, description: str = ""):
    """単語帳を作成"""
    user_id = str(interaction.user.id)
    
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # 同名の単語帳があるかチェック
        existing = await conn.fetchrow(
            "SELECT notebook_id FROM vocabulary_notebooks WHERE user_id = $1 AND name = $2",
            user_id, name
        )
        
        if existing:
            await interaction.response.send_message(
                f"❌ 既に「{name}」という名前の単語帳が存在します。",
                ephemeral=True
            )
            return
        
        # 単語帳を作成
        notebook_id = await conn.fetchval("""
            INSERT INTO vocabulary_notebooks (user_id, name, description)
            VALUES ($1, $2, $3)
            RETURNING notebook_id
        """, user_id, name, description)
    
    await interaction.response.send_message(
        f"✅ 単語帳「{name}」を作成しました！",
        ephemeral=True
    )

@discord.app_commands.command(name="notebook_add", description="単語帳に単語を追加")
async def notebook_add(
    self, 
    interaction: discord.Interaction, 
    notebook_name: str,
    word: str
):
    """単語帳に単語を追加"""
    user_id = str(interaction.user.id)
    
    # 単語が存在するか確認
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # 単語帳を取得
        notebook = await conn.fetchrow("""
            SELECT notebook_id FROM vocabulary_notebooks 
            WHERE user_id = $1 AND name = $2
        """, user_id, notebook_name)
        
        if not notebook:
            await interaction.response.send_message(
                f"❌ 単語帳「{notebook_name}」が見つかりません。",
                ephemeral=True
            )
            return
        
        # 単語を検索（部分一致でも検索できるように）
        word_row = await conn.fetchrow("""
            SELECT word_id FROM words 
            WHERE word ILIKE $1 
            LIMIT 1
        """, word)
        
        if not word_row:
            await interaction.response.send_message(
                f"❌ 単語「{word}」が見つかりません。",
                ephemeral=True
            )
            return
        
        # 既に追加されているかチェック
        existing = await conn.fetchrow("""
            SELECT * FROM notebook_words 
            WHERE notebook_id = $1 AND word_id = $2
        """, notebook['notebook_id'], word_row['word_id'])
        
        if existing:
            await interaction.response.send_message(
                f"✅ 単語「{word}」は既に単語帳に追加されています。",
                ephemeral=True
            )
            return
        
        # 追加
        await conn.execute("""
            INSERT INTO notebook_words (notebook_id, word_id)
            VALUES ($1, $2)
        """, notebook['notebook_id'], word_row['word_id'])
    
    await interaction.response.send_message(
        f"✅ 単語「{word}」を「{notebook_name}」に追加しました！",
        ephemeral=True
    )

@discord.app_commands.command(name="notebook_list", description="単語帳の一覧を表示")
async def notebook_list(self, interaction: discord.Interaction):
    """単語帳一覧を表示"""
    user_id = str(interaction.user.id)
    
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        notebooks = await conn.fetch("""
            SELECT 
                n.notebook_id,
                n.name,
                n.description,
                n.is_auto,
                COUNT(nw.word_id) as word_count
            FROM vocabulary_notebooks n
            LEFT JOIN notebook_words nw ON n.notebook_id = nw.notebook_id
            WHERE n.user_id = $1
            GROUP BY n.notebook_id, n.name, n.description, n.is_auto
            ORDER BY n.created_at DESC
        """, user_id)
    
    if not notebooks:
        await interaction.response.send_message(
            "📚 単語帳がまだありません。`/notebook_create` で作成しましょう！",
            ephemeral=True
        )
        return
    
    # Embedで表示
    embed = discord.Embed(title="📚 あなたの単語帳", color=0x2b90d9)
    
    for i, nb in enumerate(notebooks, 1):
        auto_label = " (自動更新)" if nb['is_auto'] else ""
        embed.add_field(
            name=f"{i}. 📖 {nb['name']}{auto_label}",
            value=f"{nb['word_count']}語\n{nb['description'] or '説明なし'}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
```

---

### 3. 単語帳からの学習機能

```python
async def start_from_notebook(self, interaction: discord.Interaction, notebook_name: str):
    """単語帳から学習を開始"""
    user_id = str(interaction.user.id)
    
    await ensure_defer(interaction)
    
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # 単語帳を取得
        notebook = await conn.fetchrow("""
            SELECT notebook_id FROM vocabulary_notebooks 
            WHERE user_id = $1 AND name = $2
        """, user_id, notebook_name)
        
        if not notebook:
            await interaction.followup.send(
                f"❌ 単語帳「{notebook_name}」が見つかりません。",
                ephemeral=True
            )
            return
        
        # 単語帳の単語を取得
        words = await conn.fetch("""
            SELECT w.word_id, w.word, w.jp, w.pos, w.example_en, w.example_ja, w.synonyms, w.derived
            FROM notebook_words nw
            JOIN words w ON nw.word_id = w.word_id
            WHERE nw.notebook_id = $1
            ORDER BY random()
            LIMIT 10
        """, notebook['notebook_id'])
        
        if not words or len(words) < 1:
            await interaction.followup.send(
                f"❌ 単語帳「{notebook_name}」に単語がありません。",
                ephemeral=True
            )
            return
    
    # 既存の学習フローを使用
    # vocab.py の start_ten と同様の処理
    # ただし、wordsは単語帳から取得したもの
```

---

### 4. 自動的な単語帳（苦手・復習）

#### 苦手単語帳の自動更新

```python
async def update_weak_notebook(self, user_id: str):
    """苦手単語帳を自動更新"""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # 苦手単語帳を取得または作成
        notebook = await conn.fetchrow("""
            SELECT notebook_id FROM vocabulary_notebooks 
            WHERE user_id = $1 AND name = '苦手単語帳'
        """, user_id)
        
        if not notebook:
            notebook_id = await conn.fetchval("""
                INSERT INTO vocabulary_notebooks (user_id, name, description, is_auto, auto_type)
                VALUES ($1, '苦手単語帳', '間違えた単語を自動で追加します', TRUE, 'weak')
                RETURNING notebook_id
            """, user_id)
        else:
            notebook_id = notebook['notebook_id']
            # 既存の単語を削除（リセット）
            await conn.execute("""
                DELETE FROM notebook_words WHERE notebook_id = $1
            """, notebook_id)
        
        # 間違えた単語を取得（例: 過去30日間で3回以上間違えた単語）
        weak_words = await conn.fetch("""
            SELECT DISTINCT word_id
            FROM study_logs
            WHERE user_id = $1
              AND module = 'vocab'
              AND result->>'known' = 'false'
              AND ts > NOW() - INTERVAL '30 days'
            GROUP BY word_id
            HAVING COUNT(*) >= 3
        """, user_id)
        
        # 苦手単語帳に追加
        for word in weak_words:
            await conn.execute("""
                INSERT INTO notebook_words (notebook_id, word_id)
                VALUES ($1, $2)
                ON CONFLICT (notebook_id, word_id) DO NOTHING
            """, notebook_id, word['word_id'])
```

#### 復習用単語帳の自動更新

```python
async def update_review_notebook(self, user_id: str):
    """復習用単語帳を自動更新"""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # 復習用単語帳を取得または作成
        notebook = await conn.fetchrow("""
            SELECT notebook_id FROM vocabulary_notebooks 
            WHERE user_id = $1 AND name = '復習用単語帳'
        """, user_id)
        
        if not notebook:
            notebook_id = await conn.fetchval("""
                INSERT INTO vocabulary_notebooks (user_id, name, description, is_auto, auto_type)
                VALUES ($1, '復習用単語帳', '復習が必要な単語を自動で追加します', TRUE, 'review')
                RETURNING notebook_id
            """, user_id)
        else:
            notebook_id = notebook['notebook_id']
            await conn.execute("""
                DELETE FROM notebook_words WHERE notebook_id = $1
            """, notebook_id)
        
        # 復習が必要な単語を取得（next_reviewが今日以前）
        review_words = await conn.fetch("""
            SELECT word_id
            FROM srs_state
            WHERE user_id = $1
              AND next_review <= CURRENT_DATE
            LIMIT 50
        """, user_id)
        
        # 復習用単語帳に追加
        for word in review_words:
            await conn.execute("""
                INSERT INTO notebook_words (notebook_id, word_id)
                VALUES ($1, $2)
                ON CONFLICT (notebook_id, word_id) DO NOTHING
            """, notebook_id, word['word_id'])
```

---

### 5. メニューUIへの統合

```python
# cogs/vocab.py の VocabMenuView を拡張

class VocabMenuView(discord.ui.View):
    # ... 既存のボタン ...
    
    @discord.ui.button(
        label="単語帳から学習", 
        style=discord.ButtonStyle.secondary, 
        custom_id="vocab:notebook"
    )
    async def notebook_btn(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """単語帳選択メニューを表示"""
        # ユーザーの単語帳一覧を取得
        # Select Menuで選択できるようにする
        pass
```

---

## 📊 データフロー

### 単語帳作成
```
ユーザー: /notebook_create "今週覚える単語"
→ DB: vocabulary_notebooks に追加
→ Bot: 確認メッセージ
```

### 単語追加
```
ユーザー: /notebook_add "今週覚える単語" "abandon"
→ DB: notebook_words に追加
→ Bot: 確認メッセージ
```

### 学習開始
```
ユーザー: [単語帳から学習] ボタン
→ 単語帳選択メニュー表示
→ 選択
→ notebook_words から単語を取得
→ 既存の学習フロー（vocab.py）を使用
```

---

## 🎯 実装の優先順位

### Phase 1: 基本的な機能（1-2週間）
1. ✅ データベーススキーマ追加
2. ✅ 単語帳作成・削除コマンド
3. ✅ 単語追加・削除コマンド
4. ✅ 単語帳一覧表示
5. ✅ 単語帳からの学習機能

### Phase 2: 自動的な単語帳（2-3週間）
6. ✅ 苦手単語帳の自動更新
7. ✅ 復習用単語帳の自動更新
8. ✅ 定期的な更新処理

### Phase 3: UI改善（3-4週間）
9. ✅ メニューUIへの統合
10. ✅ Select Menuでの単語帳選択
11. ✅ 単語帳の詳細表示

---

## 💡 使い方の例

### 例1: 自分で単語帳を作る

```
ユーザー: /notebook_create "今週覚える単語"
Bot: ✅ 単語帳「今週覚える単語」を作成しました！

ユーザー: /notebook_add "今週覚える単語" "abandon"
Bot: ✅ 単語「abandon」を「今週覚える単語」に追加しました！

ユーザー: [単語帳から学習] → 「今週覚える単語」を選択
→ その単語帳の単語から10問出題
```

### 例2: 苦手単語帳を使う

```
ユーザー: [単語帳から学習] → 「苦手単語帳」を選択
→ 自動で間違えた単語が集約されている
→ その単語から10問出題
```

---

## 🗄️ NGSLデータとの連携

### NGSLの3800語を使う

- 既存の `words` テーブルにNGSLの単語が入っている前提
- 単語帳機能は `words` テーブルから単語を参照
- NGSLのレベルや頻出度も活用できる

### NGSLレベル別単語帳

```
「NGSL Level 1単語帳」（最頻出語）
「NGSL Level 2単語帳」
「NGSL Level 3単語帳」
```

---

## 📝 実装時の注意点

### 1. 単語検索の改善
- 部分一致検索
- あいまい検索
- 自動補完

### 2. 単語帳の容量制限
- 1つの単語帳に最大100語など
- ユーザーごとの単語帳数の制限

### 3. パフォーマンス
- 単語帳が大きくなっても動作するように
- インデックスの最適化

---

**結論**: Discord上で単語帳を作成・管理・学習できる機能は実現可能。既存の学習機能と統合することで、ユーザーが自分の学習スタイルに合わせて単語を管理できるようになる。
