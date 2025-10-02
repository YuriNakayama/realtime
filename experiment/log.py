#!/usr/bin/env python3
"""
OpenAI Agents接続確認用の最小限のテストスクリプト
ログやエラーハンドリングは必要最低限とする
"""

from logging import INFO, Formatter, Logger, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger(name: str, log_file: str) -> Logger:
    """
    log_fileに書き込む
    """
    logger = getLogger(name)

    # 既にハンドラーが設定されている場合はそのまま返す
    if logger.hasHandlers():
        return logger

    # フォーマッターの作成
    formatter = Formatter(
        "%(levelname)s %(asctime)s - %(filename)s:l%(lineno)d - %(message)s",
        datefmt="%Y%m%d %H:%M:%S",
    )

    # コンソールハンドラーの設定
    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(INFO)
    logger.addHandler(console_handler)

    # ファイルハンドラーの設定
    # ログファイルのディレクトリを作成
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # ローテーティングファイルハンドラーの作成
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # 5個のバックアップ
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(INFO)
    logger.addHandler(file_handler)

    # ロガーのレベル設定
    logger.setLevel(INFO)

    return logger
