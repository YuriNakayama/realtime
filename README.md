# FastAPI Project

### 初期設定

```bash
# UVのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.local/bin/env

uv python pin 3.12

# 依存関係のインストール
uv sync --all-extras --dev

# 仮想環境に入る
source .venv/bin/activate
# jupyter kernelの登録
ipython kernel install --user --name=temp_fastapi
```

### サーバーの起動

```bash
uv run uvicorn src.main:app
```
