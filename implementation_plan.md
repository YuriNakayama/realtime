# Implementation Plan

[Overview]
統一的で構造化されたロギングシステムを実装し、エラーの追跡と問題の調査を容易にする。

現在のロギング実装は各モジュールで`logging.getLogger(__name__)`を個別に使用しており、一貫性がありません。この実装では、人間が読みやすい形式を維持しながら、行番号、時間、ファイル名、エラー内容等の詳細情報を含む構造化されたログフォーマットを提供します。標準出力のみに出力し、環境別の設定分離は行いません。

[Types]
新しいログ用のデータ構造と列挙型を定義する。

```python
from enum import Enum
from typing import Optional, Dict, Any

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogContext:
    session_id: Optional[str] = None
    client_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Dict[str, Any] = {}
```

[Files]
構造化ログシステムのための新規実装と既存ファイルの修正を行う。

新規作成:

- backend/src/core/log.py: カスタムフォーマッター、コンテキストフィルター、ロガー設定関数

修正対象:

- backend/src/main.py: ロギング初期化の変更
- backend/src/application/websocket_handler.py: 改善されたログ使用
- backend/src/application/session_manager.py: 改善されたログ使用
- backend/src/infrastructure/realtime_client.py: 改善されたログ使用

[Functions]
構造化ログシステムの実装に必要な関数群を定義する。

新規関数:

- setup_logging(log_level: str = "INFO") -> None: アプリケーション起動時のログ設定初期化
- get_logger(name: str) -> logging.Logger: 統一されたロガーを取得
- set_log_context(**kwargs) -> None: ログコンテキストを設定
- clear_log_context() -> None: ログコンテキストをクリア

修正関数:

- 各モジュールのlogger初期化を統一されたget_logger()に変更

[Classes]
カスタムログフォーマッターとフィルタークラスを実装する。

新規クラス:

- CustomFormatter(logging.Formatter): 構造化されたログフォーマットを提供
- ContextFilter(logging.Filter): セッションIDやリクエストIDなどのコンテキスト情報を追加
- LogContextManager: スレッドローカルなコンテキスト管理

[Dependencies]
標準ライブラリのloggingモジュールを使用し、新しい依存関係は追加しない。

既存のloggingモジュールの使用を継続し、外部依存関係は追加しません。threading.localを使用してコンテキスト管理を実装します。

[Testing]
既存のロガー利用箇所での動作確認とログフォーマットの検証を行う。

- 各モジュールでの新しいロガーの動作確認
- エラー時のスタックトレース情報確認
- コンテキスト情報の正しい表示確認
- パフォーマンスへの影響確認

[Implementation Order]
安全で段階的な実装順序でロギングシステムを構築する。

1. backend/src/core/log.pyの実装（CustomFormatter、ContextFilter、設定関数）
2. backend/src/main.pyでのロギング初期化の変更
3. backend/src/application/websocket_handler.pyでの改善されたログ使用
4. backend/src/application/session_manager.pyでの改善されたログ使用
5. backend/src/infrastructure/realtime_client.pyでの改善されたログ使用
6. 全体的な動作確認とテスト
