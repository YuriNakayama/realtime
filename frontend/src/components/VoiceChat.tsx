'use client'

import { useAudioPlayback } from '@/hooks/useAudioPlayback'
import { useAudioRecording } from '@/hooks/useAudioRecording'
import { useWebSocket } from '@/hooks/useWebSocket'
import type { TranscriptMessage } from '@/types/realtime'
import { useCallback, useEffect, useState } from 'react'

interface TranscriptEntry {
  id: string
  role: 'user' | 'assistant'
  text: string
  timestamp: Date
}

// 接続状態を管理する型
type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'disconnecting'

// ボタンの状態を管理する型
interface ButtonState {
  connect: {
    disabled: boolean
    text: string
  }
  disconnect: {
    disabled: boolean
    text: string
  }
}

// SSR対応のカスタムフック
function useSSRSafe() {
  const [isClient, setIsClient] = useState(false)
  
  useEffect(() => {
    setIsClient(true)
  }, [])
  
  return { isClient }
}

export default function VoiceChat() {
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([])
  const [errorMessage, setErrorMessage] = useState<string>('')
  const { isClient } = useSSRSafe()

  // エラーハンドラー
  const handleError = useCallback((error: string) => {
    setErrorMessage(error)
    setTimeout(() => setErrorMessage(''), 5000) // 5秒後にエラーメッセージを消去
  }, [])

  // 文字起こし追加
  const addTranscript = useCallback((role: 'user' | 'assistant', text: string) => {
    const entry: TranscriptEntry = {
      id: Date.now().toString(),
      role,
      text,
      timestamp: new Date()
    }
    setTranscript(prev => [...prev, entry])
  }, [])

  // WebSocketフック
  const {
    connectionStatus,
    connect,
    disconnect,
    sendAudio,
    commitAudio,
    interruptConversation
  } = useWebSocket({
    url: 'ws://localhost:8000/ws/realtime',
    onTranscript: (transcriptMsg: TranscriptMessage) => {
      addTranscript(transcriptMsg.role, transcriptMsg.text)
    },
    onAudioDelta: (audio: string) => {
      // OpenAIからの音声データを再生
      playAudio(audio).catch(() => {
        handleError('音声の再生に失敗しました')
      })
    },
    onError: handleError,
    autoConnect: false
  })

  // 音声再生フック
  const {
    playbackState,
    playAudio,
    stopPlayback
  } = useAudioPlayback({
    onPlaybackEnd: () => {
      console.log('Audio playback finished')
    },
    onError: handleError
  })

  // 音声録音フック
  const {
    recordingState,
    startRecording,
    stopRecording,
    isSupported: isRecordingSupported
  } = useAudioRecording({
    onAudioData: (audioData: string) => {
      // 録音された音声データをWebSocket経由で送信
      sendAudio(audioData)
    },
    onError: handleError
  })

  // 接続制御（自動音声録音開始を含む）
  const handleConnect = useCallback(async () => {
    try {
      connect()
      addTranscript('user', 'WebSocketに接続中...')
      
      // 接続後に自動で音声録音を開始
      setTimeout(async () => {
        if (connectionStatus === 'connected' && isRecordingSupported) {
          try {
            await startRecording()
            addTranscript('user', '音声録音を開始しました。お話しください。')
          } catch (error) {
            handleError('音声録音の開始に失敗しました')
          }
        }
      }, 1000) // 接続確立を待つ
    } catch (error) {
      handleError('接続に失敗しました')
    }
  }, [connect, addTranscript, connectionStatus, isRecordingSupported, startRecording, handleError])

  // 切断制御（音声処理停止を含む）
  const handleDisconnect = useCallback(() => {
    // 録音停止
    if (recordingState === 'recording') {
      stopRecording()
    }
    // 再生停止
    if (playbackState === 'playing') {
      stopPlayback()
    }
    // WebSocket切断
    disconnect()
    addTranscript('user', 'WebSocketから切断しました。')
  }, [recordingState, playbackState, stopRecording, stopPlayback, disconnect, addTranscript])

  // ボタン状態の取得
  const getButtonState = useCallback((connectionState: typeof connectionStatus): ButtonState => {
    return {
      connect: {
        disabled: connectionState === 'connecting' || connectionState === 'connected',
        text: connectionState === 'connecting' ? '接続中...' : '接続'
      },
      disconnect: {
        disabled: connectionState === 'disconnected' || connectionState === 'connecting',
        text: connectionState === 'disconnecting' ? '切断中...' : '切断'
      }
    }
  }, [])

  // 接続状態の表示テキスト
  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return '接続済み'
      case 'connecting': return '接続中...'
      case 'error': return '接続エラー'
      default: return '未接続'
    }
  }

  // 接続状態の色
  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-green-500'
      case 'connecting': return 'bg-yellow-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  // ボタン状態の取得
  const buttonState = getButtonState(connectionStatus)

  // SSRセーフなレンダリング
  if (!isClient) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6 p-4 rounded-lg bg-white shadow-sm border">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-gray-700">接続状態:</span>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-gray-500" />
                <span className="text-sm text-gray-600">読み込み中...</span>
              </div>
            </div>
            <button
              className="btn flex items-center space-x-2 px-4 py-2 text-sm bg-gray-400 text-white"
              disabled
            >
              <span>🔗</span>
              <span>読み込み中...</span>
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* エラーメッセージ */}
      {errorMessage && (
        <div className="mb-6 p-4 rounded-lg bg-red-100 border border-red-300">
          <p className="text-red-800">{errorMessage}</p>
        </div>
      )}

      {/* 簡素化された接続制御 */}
      <div className="mb-6 p-4 rounded-lg bg-white shadow-sm border">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-sm font-medium text-gray-700">接続状態:</span>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getConnectionStatusColor()}`} />
              <span className="text-sm text-gray-600">
                {getConnectionStatusText()}
              </span>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleConnect}
              className="btn flex items-center space-x-2 px-4 py-2 text-sm bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 disabled:bg-gray-400"
              disabled={buttonState.connect.disabled}
            >
              <span>🔗</span>
              <span>{buttonState.connect.text}</span>
            </button>
            <button
              onClick={handleDisconnect}
              className="btn flex items-center space-x-2 px-4 py-2 text-sm bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 disabled:bg-gray-400"
              disabled={buttonState.disconnect.disabled}
            >
              <span>⚡</span>
              <span>{buttonState.disconnect.text}</span>
            </button>
          </div>
        </div>
        
        {/* 録音サポート警告 */}
        {!isRecordingSupported && (
          <div className="mt-4 p-3 bg-yellow-100 border border-yellow-300 rounded-lg">
            <p className="text-yellow-800 text-sm">
              このブラウザは音声録音をサポートしていません
            </p>
          </div>
        )}
      </div>

      {/* 会話履歴 */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">会話履歴</h3>
        <div className="bg-gray-50 rounded-lg p-4 min-h-[300px] max-h-[500px] overflow-y-auto">
          {transcript.length > 0 ? (
            <div className="space-y-4">
              {transcript.map((entry) => (
                <div
                  key={entry.id}
                  className={`p-3 rounded-lg ${
                    entry.role === 'user' 
                      ? 'bg-blue-100 ml-8' 
                      : 'bg-green-100 mr-8'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">
                      {entry.role === 'user' ? 'あなた' : 'AI受付'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {entry.timestamp.toLocaleTimeString('ja-JP')}
                    </span>
                  </div>
                  <p className="text-gray-800 whitespace-pre-wrap">{entry.text}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center">
              「接続」ボタンを押して会話を開始してください
            </p>
          )}
        </div>
      </div>

      {/* デバッグ情報 */}
      <div className="mt-6 p-4 bg-gray-100 rounded-lg text-xs text-gray-600">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p><strong>接続状態:</strong> {connectionStatus}</p>
            <p><strong>録音状態:</strong> {recordingState}</p>
            <p><strong>再生状態:</strong> {playbackState}</p>
          </div>
          <div>
            <p><strong>音声録音サポート:</strong> {isRecordingSupported ? '有効' : '無効'}</p>
            <p><strong>会話履歴数:</strong> {transcript.length}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
