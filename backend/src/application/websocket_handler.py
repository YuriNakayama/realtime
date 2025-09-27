"""
WebSocket接続とメッセージング処理

クライアントからのWebSocket接続を管理し、OpenAI Realtime APIとの中継を行う。
"""

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from ..core.log import LogContext, clear_log_context, get_logger, set_log_context
from ..infrastructure.realtime_client import OpenAIRealtimeClient
from .models import ClientSession, RealtimeMessageType

logger = get_logger(__name__)


async def handle_websocket_connection(
    websocket: WebSocket, session: ClientSession
) -> None:
    """
    WebSocket接続を処理し、OpenAI Realtime APIとの中継を行う

    Args:
        websocket: FastAPIのWebSocketインスタンス
        session: クライアントセッション情報
    """
    realtime_client = None

    try:
        # OpenAI Realtime APIクライアントを初期化
        realtime_client = OpenAIRealtimeClient(session_id=session.session_id)
        await realtime_client.connect()

        logger.info("OpenAI Realtime API接続完了")

        # 双方向メッセージング処理を開始
        await asyncio.gather(
            handle_client_messages(websocket, session, realtime_client),
            handle_openai_messages(websocket, session, realtime_client),
        )

    except WebSocketDisconnect:
        logger.info("クライアント切断")
        raise
    except Exception as e:
        logger.error("WebSocket処理エラー", exc_info=True)
        raise
    finally:
        # OpenAI接続のクリーンアップ
        if realtime_client:
            await realtime_client.disconnect()
            logger.info("OpenAI Realtime API切断完了")


async def handle_client_messages(
    websocket: WebSocket, session: ClientSession, realtime_client: OpenAIRealtimeClient
) -> None:
    """
    クライアントからのメッセージを処理しOpenAIに転送する

    Args:
        websocket: WebSocketインスタンス
        session: セッション情報
        realtime_client: OpenAIクライアント
    """
    try:
        async for message in websocket.iter_text():
            try:
                data = json.loads(message)
                await process_client_message(data, session, realtime_client)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析エラー: {e}")
                await send_error_to_client(websocket, "Invalid JSON format")
            except Exception as e:
                logger.error(f"メッセージ処理エラー: {e}")
                await send_error_to_client(
                    websocket, f"Message processing error: {str(e)}"
                )

    except WebSocketDisconnect:
        logger.info("クライアントからのメッセージ受信終了")
        raise


async def handle_openai_messages(
    websocket: WebSocket, session: ClientSession, realtime_client: OpenAIRealtimeClient
) -> None:
    """
    OpenAIからのメッセージを処理しクライアントに転送する

    Args:
        websocket: WebSocketインスタンス
        session: セッション情報
        realtime_client: OpenAIクライアント
    """
    try:
        async for message in realtime_client.listen():
            await process_openai_message(message, websocket, session)
    except Exception as e:
        logger.error(f"OpenAIメッセージ処理エラー: {e}")
        raise


async def process_client_message(
    data: dict[str, Any], session: ClientSession, realtime_client: OpenAIRealtimeClient
) -> None:
    """
    クライアントメッセージを処理する

    Args:
        data: クライアントからのメッセージデータ
        session: セッション情報
        realtime_client: OpenAIクライアント
    """
    message_type = data.get("type")

    if message_type == "audio.append":
        # 音声データを OpenAI に送信
        audio_data = data.get("audio", "")
        await realtime_client.send_audio(audio_data)

    elif message_type == "audio.commit":
        # 音声入力完了をOpenAIに通知
        await realtime_client.commit_audio()

    elif message_type == "conversation.interrupt":
        # 会話中断をOpenAIに通知
        await realtime_client.interrupt_conversation()

    elif message_type == "session.update":
        # セッション設定更新
        config = data.get("config", {})
        await realtime_client.update_session(config)

    elif message_type == "session.create":
        # セッション作成（フロントエンドからの初期化メッセージ）
        session_config = data.get("session", {})
        if session_config:
            await realtime_client.update_session(session_config)
        logger.info("セッション初期化メッセージ受信")

    else:
        logger.warning(f"未知のメッセージタイプ: {message_type}")


async def process_openai_message(
    message: dict[str, Any], websocket: WebSocket, session: ClientSession
) -> None:
    """
    OpenAIからのメッセージを処理してクライアントに転送する

    Args:
        message: OpenAIからのメッセージ
        websocket: WebSocketインスタンス
        session: セッション情報
    """
    message_type = message.get("type")

    if message_type == "response.audio.delta":
        # 音声データをクライアントに送信
        audio_data = message.get("delta", "")
        logger.info(
            f"Sending audio.delta to client: audio_length={len(audio_data)}, session_id={session.session_id}"  # noqa: E501
        )
        await websocket.send_json(
            {
                "type": RealtimeMessageType.AUDIO_DELTA.value,
                "audio": audio_data,
                "itemId": message.get("item_id"),
                "sessionId": session.session_id,
            }
        )

    elif message_type == "response.audio.done":
        # 音声再生完了通知
        await websocket.send_json(
            {
                "type": RealtimeMessageType.AUDIO_DONE.value,
                "itemId": message.get("item_id"),
                "sessionId": session.session_id,
            }
        )

    elif message_type == "conversation.item.input_audio_transcription.completed":
        # ユーザー音声の文字起こし
        await websocket.send_json(
            {
                "type": RealtimeMessageType.TRANSCRIPT_USER.value,
                "text": message.get("transcript", ""),
                "isFinal": True,
                "sessionId": session.session_id,
            }
        )

    elif message_type == "response.text.delta":
        # AIの文字起こし（部分）
        await websocket.send_json(
            {
                "type": RealtimeMessageType.TRANSCRIPT_ASSISTANT.value,
                "text": message.get("delta", ""),
                "isFinal": False,
                "itemId": message.get("item_id"),
                "sessionId": session.session_id,
            }
        )

    elif message_type == "response.text.done":
        # AIの文字起こし（完了）
        await websocket.send_json(
            {
                "type": RealtimeMessageType.TRANSCRIPT_ASSISTANT.value,
                "text": message.get("text", ""),
                "isFinal": True,
                "itemId": message.get("item_id"),
                "sessionId": session.session_id,
            }
        )

    elif message_type == "error":
        # エラー転送
        await websocket.send_json(
            {
                "type": RealtimeMessageType.ERROR.value,
                "message": message.get("error", {}).get("message", "Unknown error"),
                "code": message.get("error", {}).get("code"),
                "sessionId": session.session_id,
            }
        )


async def send_error_to_client(websocket: WebSocket, error_message: str) -> None:
    """
    クライアントにエラーメッセージを送信する

    Args:
        websocket: WebSocketインスタンス
        error_message: エラーメッセージ
    """
    try:
        await websocket.send_json(
            {
                "type": RealtimeMessageType.ERROR.value,
                "message": error_message,
                "code": "SERVER_ERROR",
            }
        )
    except Exception as e:
        logger.error(f"エラーメッセージ送信失敗: {e}")
