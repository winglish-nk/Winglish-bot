# 🔒 セキュリティチェックリスト

## ✅ 確認済みのセキュリティ対策

### 1. 環境変数の管理

- ✅ `.env` ファイルが `.gitignore` に含まれている
- ✅ 機密情報がコードに直接書かれていない
- ✅ 環境変数の検証機能が実装されている

**確認方法:**
```bash
# .envファイルがGitに含まれていないか確認
git ls-files | grep -E "\.env$|\.env\."
# 何も出力されなければOK
```

### 2. SQLインジェクション対策

- ✅ **パラメータ化クエリを使用**: asyncpgの `$1`, `$2` プレースホルダーを使用
- ✅ **文字列フォーマットを使用していない**: `f"SELECT * FROM users WHERE id = {user_id}"` のような危険なパターンは見つかりませんでした

**良い例（現在のコード）:**
```python
# ✅ 安全: パラメータ化クエリ
await conn.fetch("SELECT * FROM users WHERE user_id = $1", user_id)

# ❌ 危険: 文字列フォーマット（使用していない）
# await conn.fetch(f"SELECT * FROM users WHERE user_id = {user_id}")  # これは使っていない
```

### 3. 入力値の検証

現在、以下の場所で入力値の検証が必要です：

**改善が必要な箇所:**
- `svocm.py`: モーダルからの入力値（S, V, O1, O2, C, M）の検証
- `admin.py`: message_id の検証（数値型チェック）

**現在の対策:**
- `admin.py` では `int(message_id)` で変換時にエラーが発生するため、基本的な検証はされている

---

## 🔍 セキュリティ強化の提案

### 1. 入力値のバリデーション強化

#### 推奨: Pydanticモデルを使用

```python
from pydantic import BaseModel, validator

class SvocmAnswer(BaseModel):
    s: str
    v: str
    o1: str | None = None
    o2: str | None = None
    c: str | None = None
    m: str | None = None
    
    @validator('s', 'v')
    def validate_required(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Required field cannot be empty')
        if len(v) > 500:
            raise ValueError('Field too long')
        return v.strip()
```

### 2. レート制限の実装

Discord APIのレート制限だけでなく、ユーザー単位のレート制限も検討：

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests: int = 10, window: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window)
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        now = datetime.utcnow()
        user_requests = self.requests[user_id]
        # ウィンドウ外のリクエストを削除
        user_requests[:] = [req_time for req_time in user_requests 
                           if now - req_time < self.window]
        
        if len(user_requests) >= self.max_requests:
            return False
        
        user_requests.append(now)
        return True
```

### 3. セキュリティヘッダーの確認

Discord Botなので直接HTTPサーバーは立てていませんが、将来追加する場合は：
- HTTPSの強制
- セキュリティヘッダーの設定
- CORS設定

---

## ✅ 現在のセキュリティ状態

### 良好な点

1. **SQLインジェクション対策**: パラメータ化クエリを使用 ✅
2. **環境変数管理**: 適切に `.gitignore` で保護 ✅
3. **エラーハンドリング**: 機密情報がログに漏れないように注意 ✅

### 改善の余地がある点

1. **入力値のバリデーション**: 一部の入力値検証を強化
2. **レート制限**: ユーザー単位のレート制限を検討
3. **セキュリティログ**: セキュリティ関連のイベントをログに記録

---

## 🔄 今後の改善計画

### 優先度高

1. **入力値のバリデーション強化**（Pydanticモデルの導入）
2. **セキュリティイベントのログ記録**

### 優先度中

3. **レート制限の実装**
4. **セキュリティ監査の定期実施**

---

## 📚 参考資料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Discord.py Security Best Practices](https://discordpy.readthedocs.io/en/stable/security.html)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/current/)

