# 頻出リストの実装方法：データ収集から表示まで

> 頻出単語リストをどうやって作るのか？データ収集、管理、表示の具体的な方法

---

## 📊 データ収集の方法

### 方法1: 参考書・問題集のデータを活用

#### アプローチ
参考書や問題集に記載されている「頻出単語リスト」を使用

#### メリット
- ✅ 既に分析されたデータ
- ✅ 信頼性が高い
- ✅ 著作権問題が少ない（単語リストは著作権の対象外）

#### デメリット
- ⚠️ 出版社の許可が必要な場合がある
- ⚠️ データの更新が難しい

#### 実装方法
```
1. 参考書の「頻出単語リスト」を手動で入力
2. 出典を明記（例: システム推奨単語帳より）
3. データベースに保存
```

---

### 方法2: ユーザーからのフィードバック

#### アプローチ
ユーザーが学習中に「この単語は〇〇大学で出た」と報告する機能

#### メリット
- ✅ 実データに基づいている
- ✅ 継続的にデータが蓄積される
- ✅ 著作権問題なし

#### デメリット
- ⚠️ 初期データがない
- ⚠️ データの精度にばらつきがある

#### 実装例
```python
# ユーザーが報告
/報告 "abandon" 早稲田 2023年

→ データベースに保存
→ 管理者が確認・承認
→ 頻出リストに反映
```

---

### 方法3: 公開されているデータを活用

#### アプローチ
- 大学が公式に公開している過去問の一部を分析
- 参考書の出版社が公開しているデータ
- 教育機関が公開している統計データ

#### 実装方法
```
1. 公開データから単語を抽出
2. 出現頻度をカウント
3. データベースに保存
```

#### 注意点
- ⚠️ 問題文全体は使わず、単語のみ抽出
- ⚠️ 出典を明記
- ⚠️ 利用規約を確認

---

### 方法4: 手動でデータを入力（管理画面）

#### アプローチ
管理者が手動でデータを入力する管理画面を作る

#### メリット
- ✅ 完全にコントロールできる
- ✅ データの品質が高い
- ✅ 著作権問題なし

#### デメリット
- ⚠️ 工数がかかる
- ⚠️ 継続的な入力が必要

#### 実装例
```
/admin/frequency/add
→ 大学名、単語、年度、出題回数を入力
→ データベースに保存
```

---

### 方法5: 既存のデータベース・APIを活用

#### アプローチ
既存の頻出単語データベースやAPIを使用

#### 例
- 教育機関が提供しているAPI
- オープンデータとして公開されているデータ

#### 注意点
- ⚠️ 利用規約を確認
- ⚠️ データの出典を明記

---

## 🗄️ データベース設計

### 基本的なテーブル設計

```sql
-- 大学情報
CREATE TABLE universities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,  -- '早稲田大学'
    short_name TEXT,  -- '早稲田'
    exam_type TEXT[],  -- ['一般入試', '共通テスト']
    created_at TIMESTAMP DEFAULT NOW()
);

-- 頻出単語データ
CREATE TABLE university_word_frequency (
    id SERIAL PRIMARY KEY,
    university_id INT REFERENCES universities(id),
    word_id INT REFERENCES words(word_id),
    appearance_count INT DEFAULT 0,  -- 出現回数
    years TEXT[],  -- 出題された年度 ['2023', '2022', '2021']
    exam_types TEXT[],  -- どの試験で出たか ['一般入試', '共通テスト']
    source TEXT,  -- データの出典 '参考書X', 'ユーザー報告', etc.
    verified BOOLEAN DEFAULT FALSE,  -- 管理者が確認済みか
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(university_id, word_id)
);

-- ユーザーからの報告（承認待ち）
CREATE TABLE word_frequency_reports (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    word_id INT REFERENCES words(word_id),
    university_id INT REFERENCES universities(id),
    exam_year TEXT,
    exam_type TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    created_at TIMESTAMP DEFAULT NOW()
);

-- 傾向データ（構文や特徴）
CREATE TABLE university_exam_trends (
    id SERIAL PRIMARY KEY,
    university_id INT REFERENCES universities(id),
    trend_type TEXT,  -- '構文', '文章の長さ', '難易度', etc.
    data JSONB,  -- 詳細データ（柔軟に保存）
    source TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 💻 実装方法

### Phase 1: 基本的なデータ入力機能

#### 1. 管理コマンドの実装

```python
# cogs/admin.py に追加

@commands.command(name="frequency_add")
@commands.has_permissions(administrator=True)
async def add_frequency(self, ctx, university: str, word: str, year: str, count: int = 1):
    """
    頻出単語データを追加
    
    例: !frequency_add 早稲田 abandon 2023 1
    """
    # データベースに保存
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # 大学IDを取得または作成
        university_id = await self._get_or_create_university(conn, university)
        
        # 単語IDを取得
        word_row = await conn.fetchrow("SELECT word_id FROM words WHERE word = $1", word)
        if not word_row:
            await ctx.send(f"❌ 単語 '{word}' が見つかりません")
            return
        
        # 頻出データを追加または更新
        await conn.execute("""
            INSERT INTO university_word_frequency 
            (university_id, word_id, appearance_count, years, source)
            VALUES ($1, $2, $3, ARRAY[$4], 'manual')
            ON CONFLICT (university_id, word_id) 
            DO UPDATE SET 
                appearance_count = university_word_frequency.appearance_count + $3,
                years = array_append(
                    array_remove(university_word_frequency.years, $4), 
                    $4
                ),
                updated_at = NOW()
        """, university_id, word_row['word_id'], count, year)
        
    await ctx.send(f"✅ '{word}' を {university} の頻出リストに追加しました")

@commands.command(name="frequency_bulk")
@commands.has_permissions(administrator=True)
async def bulk_add_frequency(self, ctx):
    """
    CSV形式で一括追加
    
    例: !frequency_bulk
    その後、CSVファイルをアップロード
    """
    # CSVファイルのアップロード機能
    pass
```

---

### Phase 2: ユーザー報告機能

```python
# cogs/vocab.py または新しい cogs/report.py に追加

@commands.Cog.listener()
async def on_interaction(self, interaction: discord.Interaction):
    # ... 既存の処理 ...
    
    if cid.startswith("vocab:report:"):
        # 「この単語は〇〇大学で出た」と報告
        word_id = int(cid.split(":")[-1])
        await self.show_report_modal(interaction, word_id)

async def show_report_modal(self, interaction: discord.Interaction, word_id: int):
    """報告モーダルを表示"""
    modal = FrequencyReportModal(word_id=word_id)
    await interaction.response.send_modal(modal)

class FrequencyReportModal(discord.ui.Modal, title="頻出単語報告"):
    university = discord.ui.TextInput(
        label="大学名",
        placeholder="例: 早稲田大学",
        required=True
    )
    exam_year = discord.ui.TextInput(
        label="年度",
        placeholder="例: 2023",
        required=True
    )
    
    def __init__(self, word_id: int):
        super().__init__()
        self.word_id = word_id
    
    async def on_submit(self, interaction: discord.Interaction):
        # データベースに保存（承認待ち）
        db_manager = get_db_manager()
        async with db_manager.acquire() as conn:
            await conn.execute("""
                INSERT INTO word_frequency_reports 
                (user_id, word_id, university_name, exam_year, status)
                VALUES ($1, $2, $3, $4, 'pending')
            """, str(interaction.user.id), self.word_id, 
                self.university.value, self.exam_year.value)
        
        await interaction.response.send_message(
            "✅ 報告ありがとうございます！管理者が確認後、反映されます。",
            ephemeral=True
        )
```

---

### Phase 3: 頻出度表示機能

```python
# cogs/vocab.py を拡張

async def show_word_with_frequency(self, interaction: discord.Interaction, word: dict):
    """単語を頻出度情報と一緒に表示"""
    
    # 頻出度データを取得
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        frequency_data = await conn.fetch("""
            SELECT 
                u.name as university_name,
                uwf.appearance_count,
                uwf.years,
                uwf.verified
            FROM university_word_frequency uwf
            JOIN universities u ON uwf.university_id = u.id
            WHERE uwf.word_id = $1
            ORDER BY uwf.appearance_count DESC
            LIMIT 5
        """, word['word_id'])
    
    # Embedに頻出度情報を追加
    desc = f"**📘 {word['word']}**\n"
    desc += f"意味：||{word['jp']}||\n"
    
    if frequency_data:
        desc += "\n**📊 頻出大学:**\n"
        for row in frequency_data:
            years_str = ", ".join(row['years'])
            verified_icon = "✅" if row['verified'] else "⏳"
            desc += f"{verified_icon} {row['university_name']}: {row['appearance_count']}回 ({years_str})\n"
    
    embed = discord.Embed(title=f"Q{self.index+1}/10", description=desc)
    # ... 残りの表示処理 ...
```

---

### Phase 4: データ管理画面（Web UI / Discordコマンド）

#### Discordコマンドベース（簡単）

```python
@commands.command(name="frequency_list")
async def list_frequency(self, ctx, university: str = None):
    """
    頻出単語リストを表示
    
    例: !frequency_list 早稲田
    """
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        if university:
            # 特定大学の頻出単語
            results = await conn.fetch("""
                SELECT w.word, uwf.appearance_count, uwf.years
                FROM university_word_frequency uwf
                JOIN words w ON uwf.word_id = w.word_id
                JOIN universities u ON uwf.university_id = u.id
                WHERE u.name LIKE $1
                ORDER BY uwf.appearance_count DESC
                LIMIT 20
            """, f"%{university}%")
        else:
            # 全体の頻出単語
            results = await conn.fetch("""
                SELECT w.word, SUM(uwf.appearance_count) as total_count
                FROM university_word_frequency uwf
                JOIN words w ON uwf.word_id = w.word_id
                GROUP BY w.word
                ORDER BY total_count DESC
                LIMIT 20
            """)
    
    # Embedで表示
    # ...
```

---

## 📋 データ収集の具体的な手順

### 初期データの構築

#### Step 1: 参考書からリストを作成
```
1. 参考書の「頻出単語リスト」を確認
   - 例: 「大学受験必須単語」「システム推奨単語帳」
   
2. データをCSV形式で整理
   早稲田, abandon, 2023, 1
   早稲田, abandon, 2022, 1
   慶應, abandon, 2023, 1
   
3. 一括インポート機能で取り込む
```

#### Step 2: ユーザー報告機能を実装
```
1. 学習中に「この単語は〇〇大学で出た」と報告できる機能
2. 報告されたデータを管理者が確認
3. 承認されたら頻出リストに反映
```

#### Step 3: 段階的にデータを蓄積
```
1. 最初は参考書のデータから開始
2. ユーザーからの報告でデータを増やす
3. 時間が経つにつれてデータが充実
```

---

## 🔄 データ更新の仕組み

### 自動化の仕組み

#### 1. ユーザー報告の自動承認（信頼性が高い場合）
```python
# 同じ報告が複数のユーザーから来たら自動承認
async def auto_approve_reports(self):
    """同じ報告が3人以上から来たら自動承認"""
    db_manager = get_db_manager()
    async with db_manager.acquire() as conn:
        # 同じ報告（大学・単語・年度）が3人以上
        results = await conn.fetch("""
            SELECT university_name, word_id, exam_year, COUNT(*) as count
            FROM word_frequency_reports
            WHERE status = 'pending'
            GROUP BY university_name, word_id, exam_year
            HAVING COUNT(*) >= 3
        """)
        
        for row in results:
            # 自動承認して頻出リストに追加
            await self._approve_report(row)
```

#### 2. 定期的なデータクリーンアップ
```python
# 古いデータを整理
async def cleanup_old_data(self):
    """5年以上前のデータは参考データとして保持"""
    # 実装
```

---

## 📊 表示方法の改善

### 単語学習時の表示

```
改善前:
Q1/10: "abandon"
意味: ||捨てる||

改善後:
【早稲田頻出】⭐️⭐️⭐️⭐️⭐️ Q1/10
📘 abandon
意味: ||捨てる||
→ 早稲田で過去5年間に3回出題
→ 年度: 2023, 2022, 2021
```

### 頻出度の可視化

```python
def get_frequency_stars(self, count: int) -> str:
    """出現回数に応じて星を表示"""
    if count >= 5:
        return "⭐️⭐️⭐️⭐️⭐️"
    elif count >= 3:
        return "⭐️⭐️⭐️⭐️"
    elif count >= 2:
        return "⭐️⭐️⭐️"
    elif count >= 1:
        return "⭐️⭐️"
    else:
        return "⭐️"
```

---

## 🚀 実装の優先順位

### Phase 1: 基本的なデータ管理（1週間）
1. ✅ データベーステーブルの作成
2. ✅ 管理コマンド（手動追加）
3. ✅ 基本的な表示機能

### Phase 2: ユーザー報告機能（2週間）
4. ✅ ユーザーが報告できる機能
5. ✅ 管理者が承認する機能
6. ✅ 報告状況の表示

### Phase 3: データの充実（継続）
7. ✅ 初期データの入力（参考書から）
8. ✅ ユーザーからの報告でデータを増やす
9. ✅ 自動承認機能（オプション）

---

## 💡 実用的な提案

### 初期データの収集方法

#### オプション1: 参考書から始める（推奨）
```
1. システム推奨単語帳などの頻出単語リストを使用
2. 「早稲田頻出」として、参考書のリストを手動で登録
3. 出典を明記（例: システム推奨単語帳より）
```

#### オプション2: ユーザーコミュニティから始める
```
1. Discordサーバーでユーザーに協力してもらう
2. 「この単語は〇〇大学で出た」と報告してもらう
3. データを蓄積していく
```

#### オプション3: 公開データを活用
```
1. 大学が公開している過去問から単語を抽出
2. 問題文は使わず、単語のみ抽出
3. 頻度をカウント
```

---

## 📝 実装例：管理コマンド

```python
# cogs/admin.py

@commands.command(name="frequency_add")
@commands.has_permissions(administrator=True)
async def add_frequency(self, ctx, university: str, word: str, year: str):
    """頻出単語を追加: !frequency_add 早稲田 abandon 2023"""
    # 実装

@commands.command(name="frequency_list")
async def list_frequency(self, ctx, university: str = None):
    """頻出単語リストを表示: !frequency_list 早稲田"""
    # 実装

@commands.command(name="frequency_report_approve")
@commands.has_permissions(administrator=True)
async def approve_report(self, ctx, report_id: int):
    """報告を承認: !frequency_report_approve 123"""
    # 実装
```

---

**結論**: 頻出リストは、参考書からの初期データ + ユーザー報告機能で段階的に構築する。まずは基本的なデータ管理機能を実装し、その後ユーザー参加型でデータを充実させていく。
