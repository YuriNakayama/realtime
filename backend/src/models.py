"""
OpenAI Realtime API用のデータモデルと型定義
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypedDict

from fastapi import WebSocket


class MessageType(Enum):
    """WebSocket通信で使用するメッセージタイプ"""

    # Client -> Server
    CLIENT_AUDIO = "client.audio"
    CLIENT_CONNECT = "client.connect"
    CLIENT_DISCONNECT = "client.disconnect"
    CLIENT_UPDATE_CONFIG = "client.update_config"
    CLIENT_INTERRUPT = "client.interrupt"

    # Server -> Client
    SERVER_AUDIO = "server.audio"
    SERVER_TRANSCRIPT = "server.transcript"
    SERVER_ERROR = "server.error"
    SERVER_STATUS = "server.status"
    SERVER_CONNECTED = "server.connected"
    SERVER_DISCONNECTED = "server.disconnected"

    # OpenAI Events
    OPENAI_SESSION_CREATED = "session.created"
    OPENAI_SESSION_UPDATED = "session.updated"
    OPENAI_CONVERSATION_CREATED = "conversation.created"
    OPENAI_INPUT_AUDIO_BUFFER_COMMITTED = "input_audio_buffer.committed"
    OPENAI_INPUT_AUDIO_BUFFER_CLEARED = "input_audio_buffer.cleared"
    OPENAI_INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"
    OPENAI_INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"
    OPENAI_CONVERSATION_ITEM_CREATED = "conversation.item.created"
    OPENAI_CONVERSATION_ITEM_TRUNCATED = "conversation.item.truncated"
    OPENAI_CONVERSATION_ITEM_DELETED = "conversation.item.deleted"
    OPENAI_RESPONSE_CREATED = "response.created"
    OPENAI_RESPONSE_DONE = "response.done"
    OPENAI_RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
    OPENAI_RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
    OPENAI_RESPONSE_CONTENT_PART_ADDED = "response.content_part.added"
    OPENAI_RESPONSE_CONTENT_PART_DONE = "response.content_part.done"
    OPENAI_RESPONSE_AUDIO_DELTA = "response.audio.delta"
    OPENAI_RESPONSE_AUDIO_TRANSCRIPT_DELTA = "response.audio_transcript.delta"
    OPENAI_RESPONSE_AUDIO_DONE = "response.audio.done"
    OPENAI_RESPONSE_AUDIO_TRANSCRIPT_DONE = "response.audio_transcript.done"
    OPENAI_ERROR = "error"


class AudioFormat(Enum):
    """音声フォーマット定義"""

    PCM16 = "pcm16"
    G711_ULAW = "g711_ulaw"
    G711_ALAW = "g711_alaw"


class VoiceType(Enum):
    """OpenAI音声タイプ"""

    ALLOY = "alloy"
    ECHO = "echo"
    SHIMMER = "shimmer"


@dataclass
class SessionConfig:
    """OpenAI Realtime APIセッション設定"""

    modalities: list[str] = field(default_factory=lambda: ["text", "audio"])
    instructions: str | None = None
    voice: str = VoiceType.ALLOY.value
    input_audio_format: str = AudioFormat.PCM16.value
    output_audio_format: str = AudioFormat.PCM16.value
    input_audio_transcription: dict[str, Any] | None = None
    turn_detection: dict[str, Any] | None = field(
        default_factory=lambda: {
            "type": "server_vad",
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 200,
        }
    )
    tools: list[dict[str, Any]] = field(default_factory=list)
    tool_choice: str = "auto"
    temperature: float = 0.8
    max_response_output_tokens: int | None = 4096


@dataclass
class ClientSession:
    """クライアントセッション情報"""

    session_id: str
    client_id: str
    websocket: WebSocket
    openai_session_id: str | None = None
    connected_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    config: SessionConfig = field(default_factory=SessionConfig)
    is_active: bool = True
    conversation_id: str | None = None
    last_activity: datetime.datetime = field(default_factory=datetime.datetime.now)


class WebSocketMessage(TypedDict):
    """WebSocketメッセージ基本構造"""

    type: str
    timestamp: str
    session_id: str | None
    data: Any


class AudioMessage(TypedDict):
    """音声データメッセージ"""

    type: str
    audio: str  # Base64 encoded PCM16 audio
    sample_rate: int
    channels: int


class TranscriptMessage(TypedDict):
    """文字起こしメッセージ"""

    type: str
    text: str
    role: str  # "user" or "assistant"
    timestamp: str
    is_final: bool


class ErrorMessage(TypedDict):
    """エラーメッセージ"""

    type: str
    error_code: str
    message: str
    details: dict[str, Any] | None


class StatusMessage(TypedDict):
    """ステータスメッセージ"""

    type: str
    status: str
    message: str
    timestamp: str


# OpenAI Realtime APIイベント用の型定義
class OpenAISessionCreated(TypedDict):
    """セッション作成イベント"""

    type: str
    session: dict[str, Any]


class OpenAIAudioResponse(TypedDict):
    """音声レスポンスイベント"""

    type: str
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    delta: str  # Base64 encoded audio


class OpenAITranscriptDelta(TypedDict):
    """文字起こしデルタイベント"""

    type: str
    response_id: str
    item_id: str
    output_index: int
    content_index: int
    delta: str


class OpenAIError(TypedDict):
    """OpenAIエラーイベント"""

    type: str
    error: dict[str, Any]


# Realtime WebSocket用の新しい型定義
class RealtimeMessageType(Enum):
    """Realtime WebSocketメッセージタイプ"""

    # クライアント → サーバー
    AUDIO_APPEND = "audio.append"
    AUDIO_COMMIT = "audio.commit"
    CONVERSATION_INTERRUPT = "conversation.interrupt"
    SESSION_UPDATE = "session.update"

    # サーバー → クライアント
    CONNECTION_ESTABLISHED = "connection.established"
    AUDIO_DELTA = "audio.delta"
    AUDIO_DONE = "audio.done"
    TRANSCRIPT_USER = "transcript.user"
    TRANSCRIPT_ASSISTANT = "transcript.assistant"
    ERROR = "error"


@dataclass
class RealtimeAudioMessage:
    """Realtime音声メッセージ"""

    type: str
    audio: str  # Base64エンコードされたPCM 16kHz 16-bit モノラル
    session_id: str


@dataclass
class RealtimeTranscriptMessage:
    """Realtime文字起こしメッセージ"""

    type: str
    text: str
    is_final: bool
    session_id: str
    item_id: str | None = None


@dataclass
class RealtimeSessionConfig:
    """Realtime セッション設定"""

    voice: str = "alloy"
    instructions: str | None = None
    temperature: float = 0.8


class RealtimeWebSocketMessage(TypedDict):
    """Realtime WebSocketメッセージ基本構造"""

    type: str
    session_id: str | None
    data: Any


class RealtimeConnectionMessage(TypedDict):
    """接続確立メッセージ"""

    type: str
    session_id: str


class RealtimeErrorMessage(TypedDict):
    """Realtimeエラーメッセージ"""

    type: str
    message: str
    code: str | None
