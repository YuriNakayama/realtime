from logging import INFO, Formatter, Logger, StreamHandler, getLogger


def get_logger(name: str) -> Logger:
    """
    ロガーを取得するユーティリティ関数
    ログの形式: ログレベル 時刻(YYYYMMDD HH:mm:ss) - エラーファイル:l行数 - メッセージ
    """
    logger = getLogger(name)
    if not logger.hasHandlers():
        handler = StreamHandler()
        formatter = Formatter(
            "%(levelname)s %(asctime)s - %(filename)s:l%(lineno)d - %(message)s",
            datefmt="%Y%m%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(INFO)
    return logger
