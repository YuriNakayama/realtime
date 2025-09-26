# バックエンドリファクタリング設計書

## 現状の構造分析

現在のディレクトリ構造：

```
backend/src/
├── main.py                 # FastAPIアプリケーションのエントリポイント
├── core/                    # 共通機能・横断的関心事
│   ├── auth_middleware.py  # 認証ミドルウェア
│   ├── auth_models.py      # 認証関連モデル
│   ├── config.py          # 設定管理
│   ├── database.py        # DynamoDBクライアント
│   ├── jwt_auth.py        # JWT認証
│   ├── logging.py         # ロギング設定
│   ├── security.py        # CORS等のセキュリティ設定
│   ├── session_manager.py # セッション管理
│   └── summary_manager.py # サマリ管理
└── reception/              # 受付機能（ドメイン）
    ├── constants.py        # 定数定義
    ├── api/               # APIエンドポイント層
    │   ├── auth.py        # 認証エンドポイント
    │   ├── router.py      # メインルーター
    │   ├── session_proxy.py # セッションプロキシ
    │   ├── summary.py     # サマリエンドポイント
    │   └── websocket.py   # WebSocketエンドポイント
    ├── infrastructure/     # インフラストラクチャ層
    │   ├── bedrock_client.py   # AWS Bedrockクライアント
    │   ├── openai_client.py    # OpenAIクライアント
    │   ├── websocket_auth.py   # WebSocket認証
    │   └── websocket_manager.py # WebSocket接続管理
    └── service/           # サービス層
        └── summary_service.py  # サマリ生成サービス
```

### 現状の特徴

- 部分的にレイヤードアーキテクチャを採用
- `core`に横断的関心事を集約
- `reception`内でapi/infrastructure/serviceの分離を実施
- ドメインモデル層が欠如
- ユースケース層が明確でない

## 提案1: クリーンアーキテクチャ

```
backend/src/
├── main.py
├── domain/                    # エンタープライズビジネスルール
│   ├── entities/             # ビジネスエンティティ
│   │   ├── session.py        # セッションエンティティ
│   │   ├── user.py          # ユーザーエンティティ
│   │   ├── message.py        # メッセージエンティティ
│   │   └── summary.py        # サマリエンティティ
│   ├── value_objects/        # 値オブジェクト
│   │   ├── session_id.py
│   │   └── user_id.py
│   └── repositories/         # リポジトリインターフェース
│       ├── session_repository.py
│       └── summary_repository.py
│
├── application/              # アプリケーションビジネスルール
│   ├── use_cases/           # ユースケース
│   │   ├── auth/
│   │   │   ├── login_use_case.py
│   │   │   └── refresh_token_use_case.py
│   │   ├── session/
│   │   │   ├── create_session_use_case.py
│   │   │   ├── get_session_use_case.py
│   │   │   └── update_session_use_case.py
│   │   └── summary/
│   │       ├── generate_summary_use_case.py
│   │       └── list_summaries_use_case.py
│   ├── dto/                 # データ転送オブジェクト
│   │   ├── auth_dto.py
│   │   ├── session_dto.py
│   │   └── summary_dto.py
│   └── services/            # アプリケーションサービス
│       ├── auth_service.py
│       └── realtime_service.py
│
├── infrastructure/          # フレームワーク＆ドライバ
│   ├── persistence/        # データ永続化
│   │   ├── dynamodb/
│   │   │   ├── session_repository_impl.py
│   │   │   └── summary_repository_impl.py
│   │   └── database.py
│   ├── external_services/  # 外部サービス
│   │   ├── openai/
│   │   │   └── openai_client.py
│   │   └── bedrock/
│   │       └── bedrock_client.py
│   ├── auth/               # 認証実装
│   │   ├── cognito_auth.py
│   │   └── jwt_handler.py
│   └── websocket/          # WebSocket実装
│       ├── connection_manager.py
│       └── websocket_handler.py
│
└── presentation/           # インターフェースアダプタ
    ├── api/               # RESTful API
    │   ├── routers/
    │   │   ├── auth_router.py
    │   │   ├── session_router.py
    │   │   └── summary_router.py
    │   ├── middleware/
    │   │   ├── auth_middleware.py
    │   │   └── cors_middleware.py
    │   └── dependencies.py
    ├── websocket/         # WebSocketエンドポイント
    │   └── realtime_endpoint.py
    └── config/            # 設定
        └── settings.py
```

### メリット

- 依存関係が明確（内側から外側への一方向）
- ビジネスロジックが外部技術から独立
- テスタビリティが高い
- 技術変更の影響が限定的

### デメリット

- ファイル数が多く複雑
- 小規模プロジェクトにはオーバーエンジニアリング
- 学習コストが高い

## 提案2: レイヤードアーキテクチャ（DDD風味）

```
backend/src/
├── main.py
├── presentation/             # プレゼンテーション層
│   ├── api/
│   │   ├── auth/
│   │   │   └── auth_controller.py
│   │   ├── session/
│   │   │   └── session_controller.py
│   │   └── summary/
│   │       └── summary_controller.py
│   ├── websocket/
│   │   └── realtime_controller.py
│   ├── middleware/
│   │   ├── auth_middleware.py
│   │   └── error_handler.py
│   └── schemas/             # リクエスト/レスポンススキーマ
│       ├── auth_schema.py
│       ├── session_schema.py
│       └── summary_schema.py
│
├── application/             # アプリケーション層
│   ├── services/           # アプリケーションサービス
│   │   ├── auth_service.py
│   │   ├── session_service.py
│   │   ├── summary_service.py
│   │   └── realtime_service.py
│   └── dto/                # DTO
│       ├── session_dto.py
│       └── summary_dto.py
│
├── domain/                  # ドメイン層
│   ├── models/             # ドメインモデル
│   │   ├── session.py
│   │   ├── user.py
│   │   ├── message.py
│   │   └── summary.py
│   ├── services/           # ドメインサービス
│   │   ├── session_domain_service.py
│   │   └── summary_generator.py
│   ├── repositories/       # リポジトリインターフェース
│   │   ├── session_repository.py
│   │   └── summary_repository.py
│   └── exceptions/         # ドメイン例外
│       └── domain_exceptions.py
│
├── infrastructure/         # インフラストラクチャ層
│   ├── persistence/       # データ永続化
│   │   ├── dynamodb_client.py
│   │   ├── session_repository_impl.py
│   │   └── summary_repository_impl.py
│   ├── external/          # 外部サービス連携
│   │   ├── openai_client.py
│   │   ├── bedrock_client.py
│   │   └── cognito_client.py
│   ├── websocket/         # WebSocket実装
│   │   └── connection_manager.py
│   └── config/            # 設定
│       ├── settings.py
│       └── logging_config.py
│
└── shared/                 # 共有コンポーネント
    ├── constants.py
    ├── utils/
    │   └── datetime_utils.py
    └── security/
        └── cors_config.py
```

### メリット

- 理解しやすい層構造
- DDDの概念を部分的に適用
- 現在の構造からの移行が容易
- 責務の分離が明確

### デメリット

- 上位層から下位層への依存がある
- ドメインロジックが他層に漏れやすい

## 提案3: ヘキサゴナルアーキテクチャ（ポート＆アダプタ）

```
backend/src/
├── main.py
├── core/                    # アプリケーションコア（ビジネスロジック）
│   ├── domain/             # ドメインモデル
│   │   ├── entities/
│   │   │   ├── session.py
│   │   │   ├── user.py
│   │   │   └── summary.py
│   │   ├── value_objects/
│   │   │   └── session_id.py
│   │   └── services/       # ドメインサービス
│   │       ├── session_service.py
│   │       └── summary_generator.py
│   │
│   ├── application/        # アプリケーションサービス
│   │   ├── commands/       # コマンド（書き込み）
│   │   │   ├── create_session.py
│   │   │   ├── update_session.py
│   │   │   └── generate_summary.py
│   │   ├── queries/        # クエリ（読み取り）
│   │   │   ├── get_session.py
│   │   │   └── list_summaries.py
│   │   └── handlers/       # コマンド/クエリハンドラ
│   │       ├── session_handler.py
│   │       └── summary_handler.py
│   │
│   └── ports/              # ポート（インターフェース）
│       ├── inbound/        # 入力ポート
│       │   ├── session_use_cases.py
│       │   └── summary_use_cases.py
│       └── outbound/       # 出力ポート
│           ├── session_repository.py
│           ├── summary_repository.py
│           ├── ai_service.py
│           └── auth_service.py
│
├── adapters/               # アダプタ（外部との接続）
│   ├── inbound/           # 入力アダプタ
│   │   ├── api/           # REST API
│   │   │   ├── auth_adapter.py
│   │   │   ├── session_adapter.py
│   │   │   └── summary_adapter.py
│   │   ├── websocket/     # WebSocket
│   │   │   └── realtime_adapter.py
│   │   └── cli/           # CLI（将来の拡張用）
│   │       └── admin_cli.py
│   │
│   └── outbound/          # 出力アダプタ
│       ├── persistence/   # データ永続化
│       │   ├── dynamodb/
│       │   │   ├── session_adapter.py
│       │   │   └── summary_adapter.py
│       │   └── memory/    # テスト用インメモリ実装
│       │       └── in_memory_adapter.py
│       ├── ai_services/   # AI サービス
│       │   ├── openai_adapter.py
│       │   └── bedrock_adapter.py
│       └── auth/          # 認証サービス
│           └── cognito_adapter.py
│
├── configuration/         # 設定と依存性注入
│   ├── dependencies.py   # 依存性注入コンテナ
│   ├── settings.py       # 設定管理
│   └── bootstrap.py      # アプリケーション起動設定
│
└── common/               # 共通ユーティリティ
    ├── exceptions.py
    ├── logging.py
    └── utils/
        └── datetime_utils.py
```

### メリット

- ビジネスロジックが中心（技術詳細から独立）
- 新しい入出力方法の追加が容易（CLI、gRPC等）
- テスト用の実装への差し替えが簡単
- CQRSパターンとの相性が良い

### デメリット

- 概念の理解が必要
- 初期設定が複雑
- 小規模プロジェクトには過剰

## 推奨事項

現在のプロジェクトの規模と複雑さを考慮すると、**提案2のレイヤードアーキテクチャ（DDD風味）** が最も適していると考えます。

### 理由

1. 現在の構造からの移行が段階的に可能
2. チームの学習コストが低い
3. 適度な複雑さでメンテナンス性が高い
4. 将来的にクリーンアーキテクチャへの移行も可能

### 移行ステップ

移行は以下の優先順位で実施することを推奨します：

1. **ドメインモデルの抽出と定義**
   - 現在のコードからビジネスエンティティを特定
   - Session, User, Message, Summaryの各ドメインモデルを作成

2. **リポジトリパターンの導入**
   - データアクセス層の抽象化
   - テスタビリティの向上

3. **アプリケーションサービスの整理**
   - ビジネスロジックの集約
   - トランザクション境界の明確化

4. **プレゼンテーション層の再構成**
   - コントローラーの責務整理
   - APIスキーマの明確化

これにより、保守性と拡張性を向上させながら、段階的にアーキテクチャを改善できます。
