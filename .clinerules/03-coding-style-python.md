# Pythonコーディングガイドライン

## 一般原則

- PEP 8準拠、Pythonic、明示的コード
- 早期リターン、単一責任、型ヒント活用

## 型ヒント・命名

- Python 3.9+標準型使用（`List`, `Optional`のようなtypingからのオブジェクトは使用せず`list[str]`, `|None`などを使用）
- 全関数引数・戻り値に型ヒント
- `TypeAlias`で複雑型定義
- Pydanticでデータ検証
- `snake_case`(関数/変数)、`PascalCase`(クラス)、`UPPER_SNAKE_CASE`(定数)
- サードパーティライブラリは必要最小限に抑える

```python
from typing import TypeAlias
from pydantic import BaseModel

UserId: TypeAlias = str

class UserData(BaseModel):
    id: UserId
    name: str
    is_active: bool = True

async def get_user(user_id: UserId) -> UserData | None:
    pass
```

## FastAPI規約

- 依存性注入活用
- Pydanticモデルでリクエスト/レスポンス定義
- 適切HTTPステータスコード使用
- 統一エラーハンドリング

```python
@app.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(request: CreateSessionRequest) -> SessionResponse:
    try:
        # 処理
        return SessionResponse(session_id="xxx", status="created")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 非同期・エラーハンドリング

- I/Oバウンド: `async`/`await`
- 並列処理: `asyncio.gather`
- 適切な例外クラス定義、ログ出力、チェーン例外使用

## テスト・ログ

- pytest使用、AAAパターン
- 構造化ログ、機密情報除外、JSON形式

## Lint/Formatting

パッケージ管理は`uv`を使用し、以下のコマンドで実行します。

```bash
- uv run ruff format .
- uv run mypy .
```
