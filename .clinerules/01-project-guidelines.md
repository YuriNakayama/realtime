# プロジェクト概要

## 基本情報

- **プロジェクト**: AI窓口（AI Reception）
- **目的**: OpenAI Realtime APIを使用したリアルタイム音声対話・受付システム
- **構成**: フロントエンドにはUIに集中し、バックエンドのみにビジネスロジックと外部APIとの連携を実装

## 技術スタック

- **フロントエンド**: Next.js 15.4+, React 19, TypeScript 5+, Tailwind CSS 4, AWS Amplify
- **バックエンド**: Python 3.12, FastAPI 0.104+, WebSockets, Uvicorn
- **インフラ**: AWS (ECS Fargate, ALB, ECR, Amplify), Terraform, Docker
- **パッケージ管理**: UV (Python), npm (Node.js)

## フォルダ構造

```plaintext
/
├── frontend/           # Next.js
│   └── src/
│       ├── app/        # Next.js App Router
│       ├── components/ # React コンポーネント
│       ├── hooks/      # カスタムフック
│       └── lib/        # ユーティリティ
├── backend/            # FastAPI
│   └── src/
│       ├── main.py     # メインアプリケーション
│       ├── core/       # 共通機能
│       └── reception/  # 受付機能
├── infra/              # Terraform IaC
│   ├── environments/   # 環境別設定
│   └── modules/        # モジュール
└── docs/              # ドキュメント
```

## 開発手順

- docs/worksのファイルを確認し、手順書がある場合はそれに従う
- 完了したタスクはチェックをつける
- ローカルでのサーバ立ち上げは既存サーバがないか確認してからおこなう。既存サーバがある場合は停止させて再起動する。
