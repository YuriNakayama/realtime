# プロジェクト概要

## 基本情報

- **プロジェクト名**: AI窓口（AI Reception）
- **目的**: OpenAI Realtime APIを使用したリアルタイム音声対話システム・受付システム
- **リポジトリURL**: <https://github.com/YuriNakayama/ai-reception.git>

## 技術スタック

- **フロントエンド**: Next.js 15.4+, React 19, TypeScript 5+, Tailwind CSS 4, AWS Amplify
- **バックエンド**: Python 3.12, FastAPI 0.104+, WebSockets, Uvicorn
- **インフラ**: AWS (ECS Fargate, ALB, ECR, Amplify), Terraform, Docker
- **リアルタイム通信**: OpenAI Realtime API, WebSockets
- **パッケージ管理**: UV (Python), npm (Node.js)
- **主要依存関係**:
  - Frontend: Next.js, React, OpenAI SDK, AWS Amplify, React Markdown, UUID
  - Backend: FastAPI, OpenAI SDK, HTTPX, Python-dotenv, boto3, PyJWT
- **開発ツール**: ESLint, TypeScript, Ruff, Mypy

## フォルダ構造

```plaintext
/
├── frontend/                    # Next.jsフロントエンド
│   ├── src/
│   │   ├── app/                # Next.js App Router
│   │   ├── components/         # Reactコンポーネント
│   │   ├── hooks/              # カスタムReact Hooks
│   │   └── lib/                # ユーティリティ関数
│   └── public/                 # 静的アセット
├── backend/                     # Pythonバックエンド
│   ├── src/
│   │   ├── main.py             # FastAPIメインアプリケーション
│   │   ├── core/               # 共通機能（認証、設定、ログ等）
│   │   └── reception/          # 受付機能（API、WebSocket、インフラ）
│   ├── tests/                  # テストコード
│   └── Dockerfile              # Dockerイメージ設定
├── infra/                      # Terraform Infrastructure as Code
│   ├── environments/           # 環境別設定
│   │   ├── dev/               # 開発環境
│   │   ├── prod/              # 本番環境
│   │   └── state/             # Terraformステート管理
│   └── modules/               # Terraformモジュール
│       ├── applications/      # アプリケーションレイヤー
│       ├── foundation/        # 基盤レイヤー（ネットワーク、DNS、セキュリティ）
│       └── platform/          # プラットフォームレイヤー（Cognito、Container、WAF等）
└── docs/                       # プロジェクトドキュメント
```
