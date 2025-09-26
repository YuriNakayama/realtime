"""
OpenAI Realtime API クライアント

OpenAI Realtime APIとの直接WebSocket接続を管理し、
音声データの送受信とセッション管理を行う。
"""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator

import websockets
from websockets.exceptions import WebSocketException

from .config import config

logger = logging.getLogger(__name__)


class OpenAIRealtimeClient:
    """OpenAI Realtime API クライアント"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.websocket: websockets.WebSocketServerProtocol | None = None
        self.is_connected = False
        
        # OpenAI Realtime API設定
        self.api_url = config.OPENAI_REALTIME_URL
        self.api_key = config.OPENAI_API_KEY
        
        # セッション設定
        self.session_config = {
            "modalities": ["text", "audio"],
            "instructions": "You are a helpful AI voice assistant. Please respond naturally and conversationally.",
            "voice": "alloy",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {"model": "whisper-1"},
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 200,
            },
            "tools": [],
            "tool_choice": "auto",
            "temperature": 0.8,
            "max_response_output_tokens": 4096,
        }
    
    async def connect(self) -> None:
        """OpenAI Realtime APIに接続する"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            logger.info(f"OpenAI Realtime API接続開始: {self.api_url}")
            
            self.websocket = await websockets.connect(
                self.api_url,
                extra_headers=headers,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10,
            )
            
            self.is_connected = True
            logger.info(f"OpenAI Realtime API接続成功: session_id={self.session_id}")
            
            # セッション初期化
            await self._initialize_session()
            
        except Exception as e:
            logger.error(f"OpenAI Realtime API接続エラー: {e}")
            self.is_connected = False
            raise
    
    async def disconnect(self) -> None:
        """OpenAI Realtime API接続を切断する"""
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
        self.is_connected = False
        logger.info(f"OpenAI Realtime API切断完了: session_id={self.session_id}")
    
    async def _initialize_session(self) -> None:
        """セッションを初期化する"""
        if not self.websocket:
            raise RuntimeError("WebSocket接続が確立されていません")
        
        session_update = {
            "type": "session.update",
            "session": self.session_config
        }
        
        await self.websocket.send(json.dumps(session_update))
        logger.info(f"セッション初期化完了: session_id={self.session_id}")
    
    async def send_audio(self, audio_base64: str) -> None:
        """音声データをOpenAIに送信する
        
        Args:
            audio_base64: Base64エンコードされた音声データ
        """
        if not self.websocket or not self.is_connected:
            raise RuntimeError("OpenAI接続が確立されていません")
        
        message = {
            "type": "input_audio_buffer.append",
            "audio": audio_base64
        }
        
        await self.websocket.send(json.dumps(message))
    
    async def commit_audio(self) -> None:
        """音声入力の完了をOpenAIに通知する"""
        if not self.websocket or not self.is_connected:
            raise RuntimeError("OpenAI接続が確立されていません")
        
        message = {
            "type": "input_audio_buffer.commit"
        }
        
        await self.websocket.send(json.dumps(message))
        
        # レスポンス生成を開始
        response_create = {
            "type": "response.create"
        }
        await self.websocket.send(json.dumps(response_create))
    
    async def interrupt_conversation(self) -> None:
        """会話を中断する"""
        if not self.websocket or not self.is_connected:
            raise RuntimeError("OpenAI接続が確立されていません")
        
        message = {
            "type": "response.cancel"
        }
        
        await self.websocket.send(json.dumps(message))
        logger.info(f"会話中断送信: session_id={self.session_id}")
    
    async def update_session(self, config: dict[str, Any]) -> None:
        """セッション設定を更新する
        
        Args:
            config: 更新する設定
        """
        if not self.websocket or not self.is_connected:
            raise RuntimeError("OpenAI接続が確立されていません")
        
        # 現在の設定を更新
        self.session_config.update(config)
        
        message = {
            "type": "session.update",
            "session": self.session_config
        }
        
        await self.websocket.send(json.dumps(message))
        logger.info(f"セッション設定更新: session_id={self.session_id}")
    
    async def listen(self) -> AsyncGenerator[dict[str, Any], None]:
        """OpenAIからのメッセージを受信する
        
        Yields:
            OpenAIからのメッセージ辞書
        """
        if not self.websocket or not self.is_connected:
            raise RuntimeError("OpenAI接続が確立されていません")
        
        try:
            async for message in self.websocket:
                if isinstance(message, str):
                    try:
                        data = json.loads(message)
                        logger.debug(f"OpenAIメッセージ受信: {data.get('type', 'unknown')}")
                        yield data
                    except json.JSONDecodeError as e:
                        logger.error(f"OpenAIメッセージJSON解析エラー: {e}")
                        continue
                else:
                    logger.warning(f"予期しないメッセージタイプ: {type(message)}")
                    
        except WebSocketException as e:
            logger.error(f"OpenAI WebSocketエラー: {e}")
            self.is_connected = False
            raise
        except Exception as e:
            logger.error(f"OpenAIメッセージ受信エラー: {e}")
            raise
    
    async def send_text_message(self, text: str) -> None:
        """テキストメッセージを送信する（テスト用）
        
        Args:
            text: 送信するテキスト
        """
        if not self.websocket or not self.is_connected:
            raise RuntimeError("OpenAI接続が確立されていません")
        
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text
                    }
                ]
            }
        }
        
        await self.websocket.send(json.dumps(message))
        
        # レスポンス生成を開始
        response_create = {
            "type": "response.create"
        }
        await self.websocket.send(json.dumps(response_create))
        
        logger.info(f"テキストメッセージ送信: session_id={self.session_id}")
    
    def is_alive(self) -> bool:
        """接続が生きているかチェックする
        
        Returns:
            接続状態
        """
        return (
            self.websocket is not None 
            and not self.websocket.closed 
            and self.is_connected
        )
