// OpenAI Realtime API用のTypeScript型定義
// バックエンドのmodels.pyと連携

export interface RealtimeMessage {
  type: string;
  sessionId?: string;
}

export interface AudioMessage extends RealtimeMessage {
  type: 'audio.append' | 'audio.delta' | 'audio.commit';
  audio?: string; // Base64 PCM data
}

export interface TranscriptMessage extends RealtimeMessage {
  type: 'transcript' | 'transcript.user' | 'transcript.assistant';
  text: string;
  role?: 'user' | 'assistant';
  isFinal?: boolean;
}

export interface ConversationMessage extends RealtimeMessage {
  type: 'conversation.interrupt' | 'conversation.item.create';
}

export interface SessionMessage extends RealtimeMessage {
  type: 'session.create' | 'session.update';
  session?: {
    modalities: string[];
    instructions: string;
    voice: string;
    input_audio_format: string;
    output_audio_format: string;
    input_audio_transcription?: {
      model: string;
    };
    turn_detection?: {
      type: string;
      threshold?: number;
      prefix_padding_ms?: number;
      silence_duration_ms?: number;
    };
  };
}

export interface ErrorMessage extends RealtimeMessage {
  type: 'error';
  error: {
    message: string;
    code?: string;
  };
}

export interface ConnectionMessage extends RealtimeMessage {
  type: 'connection.established';
}

export type WebSocketMessage = 
  | AudioMessage
  | TranscriptMessage
  | ConversationMessage
  | SessionMessage
  | ErrorMessage
  | ConnectionMessage;

// WebSocket接続状態
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

// 音声録音状態
export type RecordingState = 'idle' | 'recording' | 'processing';

// 音声再生状態
export type PlaybackState = 'idle' | 'playing' | 'paused';
