# テストコード

このディレクトリには、Winglish Botのテストコードが含まれています。

## 実行方法

### すべてのテストを実行

```bash
pytest
```

### 特定のファイルのテストを実行

```bash
pytest tests/test_srs.py
```

### カバレッジレポート付きで実行

```bash
pytest --cov=. --cov-report=html
```

生成されたレポートは `htmlcov/index.html` で確認できます。

### 詳細な出力で実行

```bash
pytest -v
```

## テストの種類

### ユニットテスト

- `test_srs.py`: SRSアルゴリズムのテスト
- `test_utils.py`: ユーティリティ関数のテスト
- `test_error_handler.py`: エラーハンドリングのテスト
- `test_config.py`: 設定管理のテスト

### マーカー

テストには以下のマーカーを使用できます：

- `@pytest.mark.unit`: ユニットテスト
- `@pytest.mark.integration`: 統合テスト
- `@pytest.mark.slow`: 時間がかかるテスト

例：

```bash
# ユニットテストのみ実行
pytest -m unit

# 遅いテストをスキップ
pytest -m "not slow"
```

## テストの追加

新しいテストを追加する際は、以下の規則に従ってください：

1. テストファイル名は `test_*.py` で始まる
2. テストクラス名は `Test*` で始まる
3. テスト関数名は `test_*` で始まる
4. 必要に応じて `conftest.py` のフィクスチャを活用する

## CI/CDでの実行

RailwayやGitHub Actionsでテストを実行する場合は、以下のコマンドを使用してください：

```bash
# 依存関係のインストール
pip install -r requirements.txt

# テストの実行
pytest --cov=. --cov-report=term
```

