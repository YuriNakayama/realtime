# Pythonコーディングガイドライン

## 一般原則

- PEP 8準拠
- Pythonicなコードにする
- 早期リターンを優先する
- 単一責任原則を守る

## 型ヒント・命名

- Python 3.9+標準型使用（`List`, `Optional`のようなtypingからのオブジェクトは使用せず`list[str]`, `|None`などを使用）
- 全関数の引数・戻り値に型ヒントをつける
- `TypeAlias`で複雑な型は定義する
- `snake_case`(関数/変数)、`PascalCase`(クラス)、`UPPER_SNAKE_CASE`(定数)
- サードパーティライブラリは必要最小限に抑える

## FastAPI規約

- 依存性注入の活用
- Pydanticモデルでリクエスト/レスポンスを定義

## 非同期・エラーハンドリング

- I/Oバウンド: `async`/`await`
- 並列処理: `asyncio.gather`
- 適切な例外クラス定義、ログ出力を行う

## テスト・ログ

- pytest使用、AAAパターン
- 構造化ログを使用し、機密情報はログに出力しない

## Lint/Formatting

パッケージ管理は`uv`を使用し、以下のコマンドで実行します。

```bash
- uv run ruff format .
- uv run mypy .
```
