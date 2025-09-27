"""
クライアントセッション管理

複数クライアントのセッション管理、タイムアウト処理、クリーンアップ機能を提供する。
シングルトンパターンで実装し、アプリケーション全体で一つのインスタンスを共有する。
"""

from __future__ import annotations

import asyncio
import datetime
import uuid
from threading import Lock
from typing import Union

from fastapi import WebSocket

from ..core.log import get_logger
from .models import ClientSession, SessionConfig

logger = get_logger(__name__)


class SessionManager:
    """
    クライアントセッション管理クラス

    複数のクライアントセッションを管理し、タイムアウト処理とクリーンアップを提供する。
    シングルトンパターンで実装されており、アプリケーション全体で一つのインスタンスを共有する。
    """

    _instance: SessionManager | None = None
    _lock: Lock = Lock()

    def __new__(cls) -> "SessionManager":
        """シングルトンパターンの実装"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """SessionManagerの初期化"""
        if not hasattr(self, "_initialized"):
            self._sessions: dict[str, ClientSession] = {}
            self._client_to_session: dict[
                str, str
            ] = {}  # client_id -> session_id のマッピング
            self._cleanup_task: asyncio.Task[None] | None = None
            self._cleanup_interval: int = 60  # 秒
            self._session_timeout: int = 300  # 5分（秒）
            self._initialized = True
            logger.info("SessionManager initialized")

    def create_session(
        self,
        client_id: str,
        websocket: WebSocket,
        config: SessionConfig | None = None,
    ) -> ClientSession:
        """
        新しいクライアントセッションを作成する

        Args:
            client_id: クライアント識別子
            websocket: WebSocket接続インスタンス
            config: セッション設定（オプション）

        Returns:
            作成されたClientSessionインスタンス

        Raises:
            ValueError: 同じclient_idで既にアクティブなセッションが存在する場合
        """
        # 既存のアクティブセッションをチェック
        if client_id in self._client_to_session:
            existing_session_id = self._client_to_session[client_id]
            existing_session = self._sessions.get(existing_session_id)
            if existing_session and existing_session.is_active:
                logger.warning(
                    f"Active session already exists for client_id: {client_id}"
                )
                raise ValueError(
                    f"Active session already exists for client_id: {client_id}"
                )

        # 新しいセッション作成
        session_id = str(uuid.uuid4())
        now = datetime.datetime.now()

        session = ClientSession(
            session_id=session_id,
            client_id=client_id,
            websocket=websocket,
            connected_at=now,
            config=config or SessionConfig(),
            is_active=True,
            last_activity=now,
        )

        self._sessions[session_id] = session
        self._client_to_session[client_id] = session_id

        logger.info(f"Created new session: {session_id} for client: {client_id}")

        # クリーンアップタスクが開始されていない場合は開始
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

        return session

    def get_session(self, session_id: str) -> ClientSession | None:
        """
        セッションIDでセッションを取得する

        Args:
            session_id: セッションID

        Returns:
            ClientSessionインスタンス、存在しない場合はNone
        """
        session = self._sessions.get(session_id)
        if session:
            logger.debug(f"Retrieved session: {session_id}")
        return session

    def get_session_by_client_id(self, client_id: str) -> ClientSession | None:
        """
        クライアントIDでセッションを取得する

        Args:
            client_id: クライアントID

        Returns:
            ClientSessionインスタンス、存在しない場合はNone
        """
        session_id = self._client_to_session.get(client_id)
        if session_id:
            return self.get_session(session_id)
        return None

    def update_session(
        self,
        session_id: str,
        **kwargs: Union[str, bool, datetime.datetime, SessionConfig],
    ) -> bool:
        """
        セッション情報を更新する

        Args:
            session_id: セッションID
            **kwargs: 更新するフィールドと値

        Returns:
            更新成功時はTrue、セッションが存在しない場合はFalse
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Session not found for update: {session_id}")
            return False

        # 許可されたフィールドのみ更新
        allowed_fields = {
            "openai_session_id",
            "config",
            "is_active",
            "conversation_id",
            "last_activity",
        }

        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(session, field):
                setattr(session, field, value)
                logger.debug(f"Updated session {session_id}: {field} = {value}")

        # last_activityを現在時刻に更新（明示的に指定されていない場合）
        if "last_activity" not in kwargs:
            session.last_activity = datetime.datetime.now()

        return True

    def update_last_activity(self, session_id: str) -> bool:
        """
        セッションの最終活動時刻を現在時刻に更新する

        Args:
            session_id: セッションID

        Returns:
            更新成功時はTrue、セッションが存在しない場合はFalse
        """
        return self.update_session(session_id, last_activity=datetime.datetime.now())

    def remove_session(self, session_id: str) -> bool:
        """
        セッションを削除する

        Args:
            session_id: 削除するセッションID

        Returns:
            削除成功時はTrue、セッションが存在しない場合はFalse
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Session not found for removal: {session_id}")
            return False

        # マッピングからも削除
        if session.client_id in self._client_to_session:
            del self._client_to_session[session.client_id]

        del self._sessions[session_id]

        logger.info(f"Removed session: {session_id} for client: {session.client_id}")
        return True

    def get_active_sessions(self) -> list[ClientSession]:
        """
        アクティブなセッションの一覧を取得する

        Returns:
            アクティブなClientSessionのリスト
        """
        active_sessions = [
            session for session in self._sessions.values() if session.is_active
        ]
        logger.debug(f"Retrieved {len(active_sessions)} active sessions")
        return active_sessions

    def get_all_sessions(self) -> list[ClientSession]:
        """
        全セッションの一覧を取得する（アクティブ・非アクティブ含む）

        Returns:
            全ClientSessionのリスト
        """
        return list(self._sessions.values())

    def get_session_count(self) -> int:
        """
        総セッション数を取得する

        Returns:
            総セッション数
        """
        return len(self._sessions)

    def get_active_session_count(self) -> int:
        """
        アクティブなセッション数を取得する

        Returns:
            アクティブなセッション数
        """
        active_count = sum(
            1 for session in self._sessions.values() if session.is_active
        )
        return active_count

    def deactivate_session(self, session_id: str) -> bool:
        """
        セッションを非アクティブにマークする（削除せず保持）

        Args:
            session_id: セッションID

        Returns:
            成功時はTrue、セッションが存在しない場合はFalse
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Session not found for deactivation: {session_id}")
            return False

        session.is_active = False
        logger.info(f"Deactivated session: {session_id}")
        return True

    def cleanup_inactive_sessions(self) -> int:
        """
        非アクティブセッションのクリーンアップを実行する

        タイムアウトした非アクティブなセッションと、
        指定時間以上活動のないセッションを削除する。

        Returns:
            削除されたセッション数
        """
        now = datetime.datetime.now()
        sessions_to_remove = []

        for session_id, session in self._sessions.items():
            # 非アクティブで一定時間経過したセッション
            if not session.is_active:
                inactive_duration = (now - session.last_activity).total_seconds()
                if inactive_duration > self._cleanup_interval:
                    sessions_to_remove.append(session_id)
                    continue

            # アクティブだが長時間活動のないセッション
            if session.is_active:
                inactive_duration = (now - session.last_activity).total_seconds()
                if inactive_duration > self._session_timeout:
                    logger.warning(
                        f"Session {session_id} timed out after {inactive_duration}s of inactivity"  # noqa: E501
                    )
                    sessions_to_remove.append(session_id)

        # セッションを削除
        removed_count = 0
        for session_id in sessions_to_remove:
            if self.remove_session(session_id):
                removed_count += 1

        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} inactive sessions")

        return removed_count

    async def _periodic_cleanup(self) -> None:
        """
        定期的なクリーンアップタスク

        バックグラウンドで実行され、定期的に非アクティブセッションを削除する。
        """
        logger.info("Started periodic cleanup task")

        try:
            while True:
                await asyncio.sleep(self._cleanup_interval)

                # アクティブなセッションが存在する場合のみクリーンアップ実行
                if self._sessions:
                    self.cleanup_inactive_sessions()
                else:
                    # セッションが存在しない場合はタスクを終了
                    logger.info("No sessions exist, stopping cleanup task")
                    break

        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled")
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")

    def set_cleanup_interval(self, interval_seconds: int) -> None:
        """
        クリーンアップ間隔を設定する

        Args:
            interval_seconds: クリーンアップ間隔（秒）
        """
        if interval_seconds > 0:
            self._cleanup_interval = interval_seconds
            logger.info(f"Cleanup interval set to {interval_seconds} seconds")
        else:
            raise ValueError("Cleanup interval must be positive")

    def set_session_timeout(self, timeout_seconds: int) -> None:
        """
        セッションタイムアウト時間を設定する

        Args:
            timeout_seconds: タイムアウト時間（秒）
        """
        if timeout_seconds > 0:
            self._session_timeout = timeout_seconds
            logger.info(f"Session timeout set to {timeout_seconds} seconds")
        else:
            raise ValueError("Session timeout must be positive")

    async def shutdown(self) -> None:
        """
        SessionManagerを安全にシャットダウンする

        クリーンアップタスクを停止し、全セッションを削除する。
        """
        logger.info("Shutting down SessionManager")

        # クリーンアップタスクを停止
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # 全セッションを削除
        session_ids = list(self._sessions.keys())
        for session_id in session_ids:
            self.remove_session(session_id)

        logger.info("SessionManager shutdown completed")

    def get_stats(self) -> dict[str, int]:
        """
        セッション統計情報を取得する

        Returns:
            統計情報を含む辞書
        """
        stats = {
            "total_sessions": len(self._sessions),
            "active_sessions": self.get_active_session_count(),
            "inactive_sessions": len(self._sessions) - self.get_active_session_count(),
            "cleanup_interval": self._cleanup_interval,
            "session_timeout": self._session_timeout,
        }
        return stats


# グローバルインスタンス（シングルトン）
session_manager = SessionManager()
