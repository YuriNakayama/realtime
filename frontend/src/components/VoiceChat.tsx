'use client'

import { useAudioPlayback } from '@/hooks/useAudioPlayback'
import { useAudioRecording } from '@/hooks/useAudioRecording'
import { useWebSocket } from '@/hooks/useWebSocket'
import type { TranscriptMessage } from '@/types/realtime'
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react'
import { useCallback, useState } from 'react'

interface TranscriptEntry {
  id: string
  role: 'user' | 'assistant'
  text: string
  timestamp: Date
}

export default function VoiceChat() {
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([])
  const [errorMessage, setErrorMessage] = useState<string>('')
  const [isRecording, setIsRecording] = useState(false)

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

  // 録音開始
  const handleStartRecording = useCallback(async () => {
    if (connectionStatus !== 'connected') {
      handleError('WebSocketが接続されていません')
      return
    }

    try {
      setIsRecording(true)
      await startRecording()
      addTranscript('user', '録音を開始しました...')
    } catch (error) {
      handleError('録音の開始に失敗しました')
      setIsRecording(false)
    }
  }, [connectionStatus, startRecording, addTranscript, handleError])

  // 録音停止
  const handleStopRecording = useCallback(() => {
    stopRecording()
    commitAudio() // 音声データのコミット
    setIsRecording(false)
    addTranscript('user', '録音を停止しました。応答を待っています...')
  }, [stopRecording, commitAudio, addTranscript])

  // 会話中断
  const handleInterrupt = useCallback(() => {
    if (isRecording) {
      stopRecording()
      setIsRecording(false)
    }
    if (playbackState === 'playing') {
      stopPlayback()
    }
    interruptConversation()
    addTranscript('user', '会話を中断しました。')
  }, [isRecording, playbackState, stopRecording, stopPlayback, interruptConversation, addTranscript])

  // 接続/切断制御
  const handleConnectionToggle = useCallback(() => {
    if (connectionStatus === 'connected') {
      disconnect()
      addTranscript('user', 'WebSocketから切断しました。')
    } else if (connectionStatus === 'disconnected' || connectionStatus === 'error') {
      connect()
      addTranscript('user', 'WebSocketに接続中...')
    }
  }, [connectionStatus, connect, disconnect, addTranscript])

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

  return (
    <div className="max-w-4xl mx-auto">
      {/* エラーメッセージ */}
      {errorMessage && (
        <div className="mb-6 p-4 rounded-lg bg-red-100 border border-red-300">
          <p className="text-red-800">{errorMessage}</p>
        </div>
      )}

      {/* 接続制御 */}
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
          <button
            onClick={handleConnectionToggle}
            className={`btn flex items-center space-x-2 px-4 py-2 text-sm ${
              connectionStatus === 'connected'
                ? 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500'
                : 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500'
            }`}
            disabled={connectionStatus === 'connecting'}
          >
            {connectionStatus === 'connected' ? (
              <>
                <span>⚡</span>
                <span>切断</span>
              </>
            ) : (
              <>
                <span>🔗</span>
                <span>接続</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* 音声コントロール */}
      <div className="card mb-6">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-6">音声コントロール</h2>
          
          <div className="flex justify-center space-x-4 mb-6">
            {!isRecording ? (
              <button
                onClick={handleStartRecording}
                className="btn-primary flex items-center space-x-2 px-8 py-4 text-lg"
                disabled={connectionStatus !== 'connected' || !isRecordingSupported}
              >
                <Mic className="w-6 h-6" />
                <span>話す</span>
              </button>
            ) : (
              <button
                onClick={handleStopRecording}
                className="btn-danger flex items-center space-x-2 px-8 py-4 text-lg"
              >
                <MicOff className="w-6 h-6" />
                <span>停止</span>
              </button>
            )}
            
            <button
              onClick={handleInterrupt}
              className="btn-secondary flex items-center space-x-2 px-6 py-4"
              disabled={!isRecording && playbackState !== 'playing'}
            >
              <VolumeX className="w-5 h-5" />
              <span>中断</span>
            </button>
          </div>

          {/* 録音インジケーター */}
          {isRecording && (
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="recording-indicator"></div>
              <span className="text-red-600 font-medium">録音中...</span>
            </div>
          )}

          {/* 再生インジケーター */}
          {playbackState === 'playing' && (
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Volume2 className="w-5 h-5 text-green-600" />
              <span className="text-green-600 font-medium">再生中...</span>
            </div>
          )}

          {/* サポート状況 */}
          {!isRecordingSupported && (
            <div className="mt-4 p-3 bg-yellow-100 border border-yellow-300 rounded-lg">
              <p className="text-yellow-800 text-sm">
                このブラウザは音声録音をサポートしていません
              </p>
            </div>
          )}
        </div>
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
              「話す」ボタンを押して会話を開始してください
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
