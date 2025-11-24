# コントリビューションガイド

Winglish Botへのコントリビューションありがとうございます！このドキュメントは、プロジェクトに貢献する際のガイドラインを提供します。

## 📋 開発環境のセットアップ

1. リポジトリをクローン
```bash
git clone https://github.com/winglish-nk/Winglish-bot.git
cd Winglish-bot
```

2. 仮想環境を作成・アクティベート
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. 依存関係をインストール
```bash
pip install -r requirements.txt
```

4. 環境変数を設定
`.env` ファイルを作成し、必要な環境変数を設定してください（`README.md`を参照）。

## 🔧 開発ガイドライン

### コードスタイル

- **型ヒント**: すべての関数に型ヒントを追加してください
- **docstring**: すべての関数とクラスにdocstringを追加してください（Googleスタイル推奨）
- **命名規則**: 
  - 関数・変数: `snake_case`
  - クラス: `PascalCase`
  - 定数: `UPPER_SNAKE_CASE`

### docstringの例

```python
def my_function(param1: str, param2: int) -> bool:
    """
    関数の短い説明
    
    Args:
        param1: パラメータ1の説明
        param2: パラメータ2の説明
        
    Returns:
        戻り値の説明
        
    Raises:
        ValueError: エラーが発生する場合の説明
    """
    pass
```

### エラーハンドリング

- `error_handler.py`の`ErrorHandler`クラスを使用してください
- エラーは適切にログに記録してください
- ユーザーには分かりやすいエラーメッセージを表示してください

### データベースアクセス

- `DatabaseManager`を使用してください（`db.py`を参照）
- パラメータ化クエリ（`$1`, `$2`など）を使用してください
- 文字列フォーマットでのSQL構築は避けてください

### テスト

- 新しい機能にはテストを追加してください
- テストは`tests/`ディレクトリに配置してください
- `pytest`でテストを実行できます

```bash
# すべてのテストを実行
pytest

# カバレッジ付きで実行
pytest --cov=. --cov-report=html
```

## 📝 コミットメッセージ

コミットメッセージは以下の形式を推奨します：

```
type(scope): 簡潔な説明

詳細な説明（必要に応じて）
```

**type（タイプ）:**
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメントのみの変更
- `style`: コードの動作に影響しない変更（フォーマットなど）
- `refactor`: バグ修正や機能追加ではないコード変更
- `test`: テストの追加・修正
- `chore`: ビルドプロセスやツールの変更

**例:**
```
feat(vocab): 単語テストのスコア表示機能を追加

- テスト終了時にスコアを表示
- 前回のスコアとの比較機能を追加
```

## 🔍 コードレビューのチェックリスト

- [ ] 型ヒントがすべての関数に追加されている
- [ ] docstringが追加されている
- [ ] エラーハンドリングが適切に実装されている
- [ ] テストが追加されている（必要に応じて）
- [ ] セキュリティのベストプラクティスに従っている
- [ ] ログが適切に記録されている

## 📚 参考資料

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Google Style Python Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

