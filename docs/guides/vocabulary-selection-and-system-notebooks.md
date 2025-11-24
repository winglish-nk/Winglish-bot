# 単語選択機能とシステム推奨単語帳の設計

## 🎯 概要

ユーザーが単語を選ぶ方法と、システムが推奨する標準的な単語帳（「ターゲット1900」的なもの）を提供する機能の設計。

---

## 1. ユーザーがwordsから単語を選ぶ方法

### 💡 検索・選択方法の選択肢

#### 方法1: テキスト検索（シンプル）

```
ユーザー: /notebook_add "今週覚える単語" word:abandon
Bot: ✅ 単語「abandon」を追加しました！
```

**実装:**
- コマンドの引数に単語を入力
- 部分一致検索（`word ILIKE '%abandon%'`）
- 複数候補がある場合は上位5件を表示して選択

**メリット:**
- ✅ シンプルで実装が簡単
- ✅ コマンドラインで完結

**デメリット:**
- ❌ 単語のスペルを正確に入力する必要がある
- ❌ 3800語から探すのが大変

---

#### 方法2: インタラクティブな検索（Select Menu）

```
ユーザー: /notebook_add "今週覚える単語"
Bot: 追加する単語を検索してください:
     [検索欄: "aban..."と入力]
     
     検索結果:
     ┌─────────────────────────┐
     │ 1. abandon (捨てる)     │
     │ 2. abandonment (放棄)   │
     └─────────────────────────┘
     [1を選択] → ✅ 追加完了
```

**実装:**
- DiscordのSelect MenuまたはAutocompleteを使用
- リアルタイムで検索候補を表示
- 選択で追加

**メリット:**
- ✅ ユーザーフレンドリー
- ✅ スペルミスが減る
- ✅ 視覚的に分かりやすい

**デメリット:**
- ❌ 実装が複雑

---

#### 方法3: ハイブリッド（推奨）

```
# 方法A: 直接入力（分かっている場合）
/notebook_add notebook:"今週覚える単語" word:abandon

# 方法B: インタラクティブ（分からない場合）
/notebook_add notebook:"今週覚える単語"
→ Select Menuで検索・選択
```

**実装:**
- まず直接入力で試す
- 見つからなかった場合、インタラクティブ検索に誘導
- Autocompleteでリアルタイム検索

---

### 🔍 検索機能の詳細設計

#### 検索方法

```python
# 部分一致検索（大文字小文字を区別しない）
SELECT word_id, word, jp, level 
FROM words 
WHERE word ILIKE '%query%' OR jp ILIKE '%query%'
ORDER BY 
  CASE WHEN word = query THEN 1
       WHEN word LIKE query || '%' THEN 2
       ELSE 3 END,
  level ASC
LIMIT 20
```

**検索対象:**
- 英単語（`word`）
- 日本語訳（`jp`）
- レベル（`level`）でフィルタリング可能

**検索優先順位:**
1. 完全一致（`word = query`）
2. 前方一致（`word LIKE 'query%'`）
3. 部分一致（`word LIKE '%query%'`）

---

#### Autocomplete実装

```python
@notebook_add.autocomplete('word')
async def word_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[discord.app_commands.Choice[str]]:
    """単語検索のAutocomplete"""
    if not current or len(current) < 2:
        # 2文字未満は検索しない（パフォーマンス）
        return []
    
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        words = await conn.fetch("""
            SELECT word, jp 
            FROM words 
            WHERE word ILIKE $1 || '%' OR jp ILIKE '%' || $1 || '%'
            ORDER BY 
              CASE WHEN word = $1 THEN 1
                   WHEN word LIKE $1 || '%' THEN 2
                   ELSE 3 END,
              level ASC
            LIMIT 25
        """, current)
    
    return [
        discord.app_commands.Choice(
            name=f"{w['word']} ({w['jp']})",
            value=w['word']
        )
        for w in words
    ]
```

---

#### Select Menu実装（検索結果の選択）

```python
class WordSelectView(discord.ui.View):
    def __init__(self, words: list[dict], notebook_id: int):
        super().__init__(timeout=60.0)
        self.notebook_id = notebook_id
        
        # Select Menuを作成
        options = [
            discord.SelectOption(
                label=f"{w['word']}",
                description=w['jp'][:100],
                value=str(w['word_id']),
                emoji="📝"
            )
            for w in words[:25]  # Discordの制限
        ]
        
        self.add_item(discord.ui.Select(
            placeholder="追加する単語を選択...",
            options=options,
            custom_id="word_select"
        ))
    
    @discord.ui.select(custom_id="word_select")
    async def word_select_callback(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        word_id = int(select.values[0])
        # 単語帳に追加
        # ...
```

---

### 📝 実装例: 検索から追加まで

```python
@discord.app_commands.command(
    name="notebook_add",
    description="単語帳に単語を追加"
)
@discord.app_commands.autocomplete(word=word_autocomplete)
async def notebook_add(
    self,
    interaction: discord.Interaction,
    notebook_name: str,
    word: str = None
) -> None:
    """単語帳に単語を追加"""
    user_id = str(interaction.user.id)
    
    # 単語が指定されていない場合、検索モードに誘導
    if not word:
        await interaction.response.send_message(
            "🔍 追加する単語を検索してください。\n"
            "`/notebook_search query:単語` で検索できます。",
            ephemeral=True
        )
        return
    
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
        
        # 単語を検索（完全一致を優先）
        word_row = await conn.fetchrow("""
            SELECT word_id, word, jp FROM words 
            WHERE word = $1
            LIMIT 1
        """, word)
        
        if not word_row:
            # 完全一致が見つからない場合、部分一致で検索
            candidates = await conn.fetch("""
                SELECT word_id, word, jp 
                FROM words 
                WHERE word ILIKE $1 || '%' OR jp ILIKE '%' || $1 || '%'
                ORDER BY 
                  CASE WHEN word = $1 THEN 1
                       WHEN word LIKE $1 || '%' THEN 2
                       ELSE 3 END
                LIMIT 10
            """, word)
            
            if not candidates:
                await interaction.response.send_message(
                    f"❌ 単語「{word}」が見つかりません。",
                    ephemeral=True
                )
                return
            
            if len(candidates) == 1:
                # 候補が1つだけなら自動で追加
                word_row = candidates[0]
            else:
                # 複数候補がある場合は選択させる
                view = WordSelectView(candidates, notebook['notebook_id'])
                await interaction.response.send_message(
                    f"🔍 「{word}」に一致する単語が複数見つかりました。",
                    view=view,
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
                f"✅ 単語「{word_row['word']}」は既に単語帳に追加されています。",
                ephemeral=True
            )
            return
        
        # 追加
        await conn.execute("""
            INSERT INTO notebook_words (notebook_id, word_id)
            VALUES ($1, $2)
        """, notebook['notebook_id'], word_row['word_id'])
    
    await interaction.response.send_message(
        f"✅ 単語「{word_row['word']} ({word_row['jp']})」を「{notebook_name}」に追加しました！",
        ephemeral=True
    )
```

---

## 2. システム推奨単語帳（「ターゲット1900」的なもの）

### 💡 システム推奨単語帳とは

システムが全ユーザーに提供する標準的な単語帳。例:
- 「NGSL Level 1」（最頻出語）
- 「NGSL Level 2」
- 「NGSL Level 3」
- 「ターゲット1900」（大学受験頻出語）

**特徴:**
- ✅ 全ユーザーが同じ単語帳を利用できる
- ✅ システム管理者が作成・管理
- ✅ ユーザーは「この単語帳をフォローする」だけで使える
- ✅ ユーザーは削除できないが、学習は自由にできる

---

### 🗄️ データベース設計

```sql
-- 単語帳テーブル（システム推奨フラグを追加）
CREATE TABLE IF NOT EXISTS vocabulary_notebooks (
    notebook_id SERIAL PRIMARY KEY,
    user_id TEXT,  -- NULLの場合はシステム推奨
    name TEXT NOT NULL,
    description TEXT,
    is_auto BOOLEAN DEFAULT FALSE,
    auto_type TEXT,
    is_system BOOLEAN DEFAULT FALSE,  -- システム推奨かどうか
    system_type TEXT,  -- 'ngsl_level1', 'ngsl_level2', 'target1900', etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, name)  -- user_idがNULLの場合はシステム推奨として一意
);

-- システム推奨単語帳の単語（全ユーザー共通）
CREATE TABLE IF NOT EXISTS system_notebook_words (
    notebook_id INT NOT NULL REFERENCES vocabulary_notebooks(notebook_id) ON DELETE CASCADE,
    word_id INT NOT NULL REFERENCES words(word_id) ON DELETE CASCADE,
    order_index INT,  -- 学習順序
    added_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY(notebook_id, word_id)
);

-- ユーザーがシステム推奨単語帳を「フォロー」する（個人用コピー）
CREATE TABLE IF NOT EXISTS user_notebook_subscriptions (
    user_id TEXT NOT NULL,
    notebook_id INT NOT NULL REFERENCES vocabulary_notebooks(notebook_id) ON DELETE CASCADE,
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY(user_id, notebook_id)
);
```

**設計のポイント:**
- `user_id` が `NULL` = システム推奨単語帳
- `user_id` が設定されている = ユーザー個人の単語帳
- システム推奨単語帳は `system_notebook_words` に単語を保存（全ユーザー共通）
- ユーザーが「フォロー」すると、`user_notebook_subscriptions` に記録

---

### 📊 データ構造の例

```sql
-- システム推奨単語帳の作成
INSERT INTO vocabulary_notebooks (user_id, name, description, is_system, system_type)
VALUES (NULL, 'NGSL Level 1', 'NGSL最頻出語（約1000語）', TRUE, 'ngsl_level1');

INSERT INTO vocabulary_notebooks (user_id, name, description, is_system, system_type)
VALUES (NULL, 'ターゲット1900', '大学受験頻出語1900語', TRUE, 'target1900');

-- システム推奨単語帳に単語を追加
INSERT INTO system_notebook_words (notebook_id, word_id, order_index)
SELECT 1, word_id, row_number() OVER (ORDER BY level, word_id)
FROM words 
WHERE level = 1 
ORDER BY level, word_id
LIMIT 1000;

-- ユーザーがシステム推奨単語帳をフォロー
INSERT INTO user_notebook_subscriptions (user_id, notebook_id)
VALUES ('user123', 1);
```

---

### 🎨 UI/UX設計

#### システム推奨単語帳の一覧表示

```
📚 システム推奨単語帳

1. 📖 NGSL Level 1 (1000語) ⭐
   最頻出語を効率的に学習
   [フォローする] [学習する]

2. 📖 NGSL Level 2 (1000語)
   中級者向けの重要語
   [フォローする] [学習する]

3. 📖 ターゲット1900 (1900語) ⭐
   大学受験頻出語
   [フォローする] [学習する]
```

**表示方法:**
- システム推奨単語帳は `is_system = TRUE` で識別
- `user_id = NULL` なので、全ユーザーに同じものが表示される
- 「フォロー」ボタンで個人用コピーを作成
- 「学習する」ボタンでそのまま学習可能

---

### 🔄 フォロー機能の実装

```python
@discord.app_commands.command(
    name="notebook_follow",
    description="システム推奨単語帳をフォローする"
)
async def notebook_follow(
    self,
    interaction: discord.Interaction,
    notebook_name: str
) -> None:
    """システム推奨単語帳をフォロー"""
    user_id = str(interaction.user.id)
    
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # システム推奨単語帳を取得
        system_notebook = await conn.fetchrow("""
            SELECT notebook_id, name, description 
            FROM vocabulary_notebooks 
            WHERE is_system = TRUE AND name = $1
        """, notebook_name)
        
        if not system_notebook:
            await interaction.response.send_message(
                f"❌ システム推奨単語帳「{notebook_name}」が見つかりません。",
                ephemeral=True
            )
            return
        
        # 既にフォローしているかチェック
        existing = await conn.fetchrow("""
            SELECT * FROM user_notebook_subscriptions 
            WHERE user_id = $1 AND notebook_id = $2
        """, user_id, system_notebook['notebook_id'])
        
        if existing:
            await interaction.response.send_message(
                f"✅ 既に「{notebook_name}」をフォローしています。",
                ephemeral=True
            )
            return
        
        # フォロー
        await conn.execute("""
            INSERT INTO user_notebook_subscriptions (user_id, notebook_id)
            VALUES ($1, $2)
        """, user_id, system_notebook['notebook_id'])
        
        # 単語数を取得
        word_count = await conn.fetchval("""
            SELECT COUNT(*) FROM system_notebook_words 
            WHERE notebook_id = $1
        """, system_notebook['notebook_id'])
    
    await interaction.response.send_message(
        f"✅ 「{notebook_name}」({word_count}語) をフォローしました！\n"
        f"これで「{notebook_name}」から学習できます。",
        ephemeral=True
    )
```

---

### 📚 システム推奨単語帳から学習

```python
async def start_from_notebook(
    self,
    interaction: discord.Interaction,
    notebook_name: str
) -> None:
    """単語帳から学習を開始（システム推奨も含む）"""
    user_id = str(interaction.user.id)
    
    await ensure_defer(interaction)
    
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # 単語帳を取得（システム推奨もユーザー個人のも含む）
        notebook = await conn.fetchrow("""
            SELECT notebook_id, is_system, user_id 
            FROM vocabulary_notebooks 
            WHERE name = $1 
              AND (
                  is_system = TRUE 
                  OR user_id = $2
              )
        """, notebook_name, user_id)
        
        if not notebook:
            await interaction.followup.send(
                f"❌ 単語帳「{notebook_name}」が見つかりません。",
                ephemeral=True
            )
            return
        
        # システム推奨の場合
        if notebook['is_system']:
            words = await conn.fetch("""
                SELECT w.word_id, w.word, w.jp, w.pos, w.example_en, w.example_ja
                FROM system_notebook_words snw
                JOIN words w ON snw.word_id = w.word_id
                WHERE snw.notebook_id = $1
                ORDER BY snw.order_index, random()
                LIMIT 10
            """, notebook['notebook_id'])
        else:
            # ユーザー個人の単語帳の場合
            words = await conn.fetch("""
                SELECT w.word_id, w.word, w.jp, w.pos, w.example_en, w.example_ja
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
    items = [dict(r) for r in words]
    batch_id = str(uuid.uuid4())
    view = VocabSessionView(batch_id, items)
    await safe_edit(interaction, embed=discord.Embed(title=f"英単語 10問 - {notebook_name}"), view=None)
    await view.send_current(interaction)
    
    # セッションバッチを記録
    async with db_manager.acquire() as conn:
        await conn.execute(
            "INSERT INTO session_batches(user_id, module, batch_id) VALUES($1,$2,$3) ON CONFLICT DO NOTHING",
            user_id, "vocab", batch_id
        )
```

---

### 🎯 システム推奨単語帳の作成スクリプト

```python
# scripts/create_system_notebooks.py

async def create_system_notebooks():
    """システム推奨単語帳を作成"""
    db_manager = get_db_manager()
    await db_manager.initialize()
    
    async with db_manager.acquire() as conn:
        # NGSL Level 1を作成
        notebook_id = await conn.fetchval("""
            INSERT INTO vocabulary_notebooks (user_id, name, description, is_system, system_type)
            VALUES (NULL, 'NGSL Level 1', 'NGSL最頻出語（約1000語）', TRUE, 'ngsl_level1')
            RETURNING notebook_id
        """)
        
        # Level 1の単語を追加
        await conn.execute("""
            INSERT INTO system_notebook_words (notebook_id, word_id, order_index)
            SELECT $1, word_id, row_number() OVER (ORDER BY level, word_id) as order_index
            FROM words 
            WHERE level = 1 
            ORDER BY level, word_id
            LIMIT 1000
        """, notebook_id)
        
        # ターゲット1900を作成（例：level 1と2を組み合わせ）
        notebook_id_target = await conn.fetchval("""
            INSERT INTO vocabulary_notebooks (user_id, name, description, is_system, system_type)
            VALUES (NULL, 'ターゲット1900', '大学受験頻出語1900語', TRUE, 'target1900')
            RETURNING notebook_id
        """)
        
        await conn.execute("""
            INSERT INTO system_notebook_words (notebook_id, word_id, order_index)
            SELECT $1, word_id, row_number() OVER (ORDER BY level, word_id) as order_index
            FROM words 
            WHERE level IN (1, 2)
            ORDER BY level, word_id
            LIMIT 1900
        """, notebook_id_target)
    
    print("✅ システム推奨単語帳を作成しました")
```

---

## 📋 まとめ

### 単語選択機能
1. **Autocomplete** でリアルタイム検索
2. **Select Menu** で候補から選択
3. **部分一致検索** で柔軟に検索

### システム推奨単語帳
1. **NGSL Level 1, 2, 3** などの標準的な単語帳
2. **ターゲット1900** などの大学受験向け単語帳
3. ユーザーが「フォロー」して利用
4. 全ユーザーに同じ単語帳を提供

これで、ユーザーは効率的に単語を選べ、システム推奨の単語帳も活用できます！
