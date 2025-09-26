import type {
  AudioMessage,
  ConnectionStatus,
  ConversationMessage,
  ErrorMessage,
  TranscriptMessage,
  WebSocketMessage
} from '@/types/realtime';
import { useCallback, useEffect, useRef, useState } from 'react';

interface UseWebSocketProps {
  url: string;
  onMessage?: (message: WebSocketMessage) => void;
  onAudioDelta?: (audio: string) => void;
  onTranscript?: (transcript: TranscriptMessage) => void;
  onError?: (error: string) => void;
  autoConnect?: boolean;
}

interface UseWebSocketReturn {
  connectionStatus: ConnectionStatus;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: WebSocketMessage) => void;
  sendAudio: (audioData: string) => void;
  commitAudio: () => void;
  interruptConversation: () => void;
}

export const useWebSocket = ({
  url,
  onMessage,
  onAudioDelta,
  onTranscript,
  onError,
  autoConnect = false
}: UseWebSocketProps): UseWebSocketReturn => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const sessionIdRef = useRef<string | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionStatus('connecting');

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        
        // セッション作成メッセージを送信
        const sessionMessage = {
          type: 'session.create',
          session: {
            modalities: ['text', 'audio'],
            instructions: 'あなたは受付担当のAIアシスタントです。来客の要件を聞いて、適切に対応してください。',
            voice: 'alloy',
            input_audio_format: 'pcm16',
            output_audio_format: 'pcm16',
            input_audio_transcription: {
              model: 'whisper-1'
            },
            turn_detection: {
              type: 'server_vad',
              threshold: 0.5,
              prefix_padding_ms: 300,
              silence_duration_ms: 500
            }
          }
        };
        ws.send(JSON.stringify(sessionMessage));
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('Received message:', message);

          // セッションIDを保存
          if (message.sessionId) {
            sessionIdRef.current = message.sessionId;
          }

          // メッセージタイプ別処理
          switch (message.type) {
            case 'audio.delta':
              const audioMsg = message as AudioMessage;
              if (audioMsg.audio && onAudioDelta) {
                onAudioDelta(audioMsg.audio);
              }
              break;

            case 'transcript.user':
            case 'transcript.assistant':
              const transcriptMsg = message as TranscriptMessage;
              if (onTranscript) {
                onTranscript(transcriptMsg);
              }
              break;

            case 'connection.established':
              console.log('WebSocket connection established:', message);
              break;

            case 'error':
              const errorMsg = message as ErrorMessage;
              // バックエンドエラーをフロントエンド用にマスク
              if (onError) {
                onError('処理中にエラーが発生しました。もう一度お試しください');
              }
              break;

            default:
              console.log('Unknown message type received:', message);
              if (onMessage) {
                onMessage(message);
              }
          }
        } catch (error) {
          // バックエンドエラーをフロントエンド用にマスク
          if (onError) {
            onError('データの処理中にエラーが発生しました');
          }
        }
      };

      ws.onerror = (error) => {
        // バックエンドエラーをフロントエンド用にマスク
        setConnectionStatus('error');
        if (onError) {
          onError('接続に問題が発生しました。しばらく時間をおいて再度お試しください');
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setConnectionStatus('disconnected');
        wsRef.current = null;
      };

    } catch (error) {
      // バックエンドエラーをフロントエンド用にマスク
      setConnectionStatus('error');
      if (onError) {
        onError('接続の開始に失敗しました。ネットワーク接続をご確認ください');
      }
    }
  }, [url, onMessage, onAudioDelta, onTranscript, onError, autoConnect]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'User initiated disconnect');
      wsRef.current = null;
    }

    sessionIdRef.current = null;
    setConnectionStatus('disconnected');
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      // セッションIDを追加
      if (sessionIdRef.current) {
        message.sessionId = sessionIdRef.current;
      }
      wsRef.current.send(JSON.stringify(message));
    } else {
      if (onError) {
        onError('接続が確立されていません。再接続をお試しください');
      }
    }
  }, [onError]);

  const sendAudio = useCallback((audioData: string) => {
    const message: AudioMessage = {
      type: 'audio.append',
      audio: audioData
    };
    sendMessage(message);
  }, [sendMessage]);

  const commitAudio = useCallback(() => {
    const message: AudioMessage = {
      type: 'audio.commit'
    };
    sendMessage(message);
  }, [sendMessage]);

  const interruptConversation = useCallback(() => {
    const message: ConversationMessage = {
      type: 'conversation.interrupt'
    };
    sendMessage(message);
  }, [sendMessage]);

  // 自動接続
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect]); // connectとdisconnectを依存配列から削除

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return {
    connectionStatus,
    connect,
    disconnect,
    sendMessage,
    sendAudio,
    commitAudio,
    interruptConversation
  };
};
