"""
構造化ロギングシステム

統一的で構造化されたログフォーマットを提供し、
デバッグとエラー追跡を容易にする。
"""

import logging
import sys
import threading
from typing import Any, Dict, Optional


class LogContextManager:
    """スレッドローカルなログコンテキスト管理"""

    def __init__(self):
        self._local = threading.local()

    def set_context(self, **kwargs: Any) -> None:
        """ログコンテキストを設定"""
        if not hasattr(self._local, "context"):
            self._local.context = {}
        self._local.context.update(kwargs)

    def get_context(self) -> Dict[str, Any]:
        """現在のログコンテキストを取得"""
        if hasattr(self._local, "context"):
            return self._local.context.copy()
        return {}

    def clear_context(self) -> None:
        """ログコンテキストをクリア"""
        if hasattr(self._local, "context"):
            self._local.context.clear()

    def remove_context_key(self, key: str) -> None:
        """特定のコンテキストキーを削除"""
        if hasattr(self._local, "context") and key in self._local.context:
            del self._local.context[key]


# グローバルコンテキストマネージャー
_context_manager = LogContextManager()


class ContextFilter(logging.Filter):
    """ログレコードにコンテキスト情報を追加するフィルター"""

    def filter(self, record: logging.LogRecord) -> bool:
        """ログレコードにコンテキスト情報を追加"""
        context = _context_manager.get_context()

        # コンテキスト情報をレコードに追加
        record.session_id = context.get("session_id", "")
        record.client_id = context.get("client_id", "")
        record.request_id = context.get("request_id", "")

        # 追加データがある場合は文字列化
        additional_data = context.get("additional_data", {})
        if additional_data:
            additional_parts = []
            for key, value in additional_data.items():
                additional_parts.append(f'{key}="{value}"')
            record.additional_context = " | ".join(additional_parts)
        else:
            record.additional_context = ""

        return True


class CustomFormatter(logging.Formatter):
    """構造化されたログフォーマッター"""

    def __init__(self):
        super().__init__()

        # 日時フォーマット（分まで）
        self.datefmt = "%Y-%m-%d %H:%M"

        # シンプルフォーマット（モジュール名と追加情報なし）
        self.simple_format = (
            "%(asctime)s | %(levelname)-8s | "
            "%(pathname)s:%(lineno)d | %(funcName)s() | %(message)s"
        )

    def format(self, record: logging.LogRecord) -> str:
        """ログレコードをフォーマット"""
        formatter = logging.Formatter(self.simple_format, self.datefmt)
        return formatter.format(record)


def setup_logging(log_level: str = "INFO") -> None:
    """
    アプリケーション全体のロギング設定を初期化

    Args:
        log_level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    """

    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # コンソールハンドラーの作成
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # カスタムフォーマッターとフィルターを設定
    console_handler.setFormatter(CustomFormatter())
    console_handler.addFilter(ContextFilter())

    # ハンドラーをルートロガーに追加
    root_logger.addHandler(console_handler)

    # 外部ライブラリのログレベルを調整
    # websocketsライブラリは詳細すぎるため、WARNINGに設定
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # 設定完了ログ
    logger = logging.getLogger("log_setup")
    logger.info(f"ロギングシステム初期化完了: level={log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    統一されたロガーを取得

    Args:
        name: ロガー名（通常は __name__ を使用）

    Returns:
        設定済みのロガーインスタンス
    """
    return logging.getLogger(name)


def set_log_context(**kwargs: Any) -> None:
    """
    ログコンテキストを設定

    Args:
        **kwargs: コンテキスト情報（session_id, client_id, request_id, additional_data等）

    Examples:
        set_log_context(session_id="abc123", client_id="user456")
        set_log_context(additional_data={"operation": "audio_processing"})
    """  # noqa: E501
    _context_manager.set_context(**kwargs)


def clear_log_context() -> None:
    """ログコンテキストをクリア"""
    _context_manager.clear_context()


def remove_log_context_key(key: str) -> None:
    """
    特定のコンテキストキーを削除

    Args:
        key: 削除するコンテキストキー
    """
    _context_manager.remove_context_key(key)


def get_log_context() -> Dict[str, Any]:
    """
    現在のログコンテキストを取得

    Returns:
        現在のコンテキスト情報
    """
    return _context_manager.get_context()


class LogContext:
    """ログコンテキストを一時的に設定するコンテキストマネージャー"""

    def __init__(self, **kwargs: Any):
        self.context = kwargs
        self.original_context: Optional[Dict[str, Any]] = None

    def __enter__(self):
        # 現在のコンテキストをバックアップ
        self.original_context = get_log_context()
        # 新しいコンテキストを設定
        set_log_context(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 元のコンテキストを復元
        clear_log_context()
        if self.original_context:
            set_log_context(**self.original_context)


# 使用例とテスト用の関数
def _test_logging():
    """ロギングシステムのテスト用関数"""

    setup_logging("DEBUG")
    logger = get_logger("test_logger")

    # 基本ログ
    logger.info("基本的なログメッセージ")

    # コンテキスト付きログ
    set_log_context(session_id="test_session_123", client_id="test_client_456")
    logger.info("セッションコンテキスト付きログ")

    # 追加データ付きログ
    set_log_context(additional_data={"operation": "test", "duration": "100ms"})
    logger.warning("追加データ付きログ")

    # エラーログ
    try:
        raise ValueError("テストエラー")
    except ValueError:
        logger.error("エラーが発生しました", exc_info=True)

    # コンテキストマネージャーのテスト
    with LogContext(session_id="context_manager_test"):
        logger.info("コンテキストマネージャーテスト")

    # コンテキストクリア
    clear_log_context()
    logger.info("コンテキストクリア後のログ")


if __name__ == "__main__":
    _test_logging()
