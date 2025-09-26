"""
アプリケーション設定管理
"""

import os

from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()


class Config:
    """アプリケーション設定クラス"""

    # OpenAI API設定
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_REALTIME_URL: str = os.getenv(
        "OPENAI_REALTIME_URL",
        "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01",
    )

    # サーバー設定
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    # セッション管理設定
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    MAX_CONCURRENT_SESSIONS: int = int(os.getenv("MAX_CONCURRENT_SESSIONS", "100"))
    CLEANUP_INTERVAL_SECONDS: int = int(os.getenv("CLEANUP_INTERVAL_SECONDS", "300"))

    # 音声設定
    DEFAULT_SAMPLE_RATE: int = int(os.getenv("DEFAULT_SAMPLE_RATE", "24000"))
    DEFAULT_CHANNELS: int = int(os.getenv("DEFAULT_CHANNELS", "1"))
    AUDIO_CHUNK_SIZE: int = int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))

    # WebSocket設定
    WEBSOCKET_PING_INTERVAL: int = int(os.getenv("WEBSOCKET_PING_INTERVAL", "20"))
    WEBSOCKET_PING_TIMEOUT: int = int(os.getenv("WEBSOCKET_PING_TIMEOUT", "10"))
    WEBSOCKET_CLOSE_TIMEOUT: int = int(os.getenv("WEBSOCKET_CLOSE_TIMEOUT", "10"))

    # CORS設定
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")

    @classmethod
    def validate_config(cls) -> None:
        """設定値の検証"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

        if not cls.OPENAI_REALTIME_URL.startswith("wss://"):
            raise ValueError("OPENAI_REALTIME_URL must start with wss://")

        if cls.PORT < 1 or cls.PORT > 65535:
            raise ValueError("PORT must be between 1 and 65535")

        if cls.SESSION_TIMEOUT_MINUTES < 1:
            raise ValueError("SESSION_TIMEOUT_MINUTES must be at least 1")

        if cls.MAX_CONCURRENT_SESSIONS < 1:
            raise ValueError("MAX_CONCURRENT_SESSIONS must be at least 1")


# グローバル設定インスタンス
config = Config()
