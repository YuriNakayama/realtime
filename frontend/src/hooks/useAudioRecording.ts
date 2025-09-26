import { useRef, useCallback, useState } from 'react';
import type { RecordingState } from '@/types/realtime';

interface UseAudioRecordingProps {
  onAudioData?: (audioData: string) => void;
  onError?: (error: string) => void;
}

interface UseAudioRecordingReturn {
  recordingState: RecordingState;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  isSupported: boolean;
}

export const useAudioRecording = ({
  onAudioData,
  onError
}: UseAudioRecordingProps): UseAudioRecordingReturn => {
  const [recordingState, setRecordingState] = useState<RecordingState>('idle');
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Web Audio APIサポート確認
  const isSupported = typeof window !== 'undefined' && 
    'navigator' in window && 
    'mediaDevices' in navigator && 
    'getUserMedia' in navigator.mediaDevices;

  // PCM16データをBase64に変換
  const pcmToBase64 = useCallback((buffer: Float32Array): string => {
    // Float32Array (-1.0 to 1.0) を Int16Array (-32768 to 32767) に変換
    const int16Array = new Int16Array(buffer.length);
    for (let i = 0; i < buffer.length; i++) {
      // -1.0から1.0の値を-32768から32767にスケール
      int16Array[i] = Math.max(-32768, Math.min(32767, buffer[i] * 32767));
    }
    
    // Int16ArrayをUint8Arrayに変換（リトルエンディアン）
    const uint8Array = new Uint8Array(int16Array.buffer);
    
    // Base64エンコード
    let binary = '';
    for (let i = 0; i < uint8Array.length; i++) {
      binary += String.fromCharCode(uint8Array[i]);
    }
    return btoa(binary);
  }, []);

  const startRecording = useCallback(async (): Promise<void> => {
    if (!isSupported) {
      const errorMsg = 'このブラウザは音声録音をサポートしていません';
      console.error(errorMsg);
      if (onError) onError(errorMsg);
      return;
    }

    if (recordingState === 'recording') {
      return;
    }

    try {
      setRecordingState('recording');

      // マイクアクセス許可を要求
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000, // 16kHz
          channelCount: 1,   // モノラル
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      streamRef.current = stream;

      // AudioContextを作成
      const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      const audioContext = new AudioContextClass({
        sampleRate: 16000
      });
      audioContextRef.current = audioContext;

      // メディアストリームソースを作成
      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;

      // アナライザーを作成（音声レベル監視用）
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;

      // ScriptProcessorNode を作成（リアルタイム音声処理）
      const processor = audioContext.createScriptProcessor(1024, 1, 1);
      processorRef.current = processor;

      // 音声データ処理
      processor.onaudioprocess = (event) => {
        const inputBuffer = event.inputBuffer.getChannelData(0);
        
        // 音声データをBase64に変換して送信
        if (onAudioData) {
          const base64Audio = pcmToBase64(inputBuffer);
          onAudioData(base64Audio);
        }
      };

      // AudioNodeを接続
      source.connect(analyser);
      analyser.connect(processor);
      processor.connect(audioContext.destination);

      console.log('Recording started');

    } catch (error) {
      console.error('Failed to start recording:', error);
      setRecordingState('idle');
      
      let errorMsg = '録音の開始に失敗しました';
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          errorMsg = 'マイクアクセスが拒否されました。ブラウザの設定でマイクアクセスを許可してください。';
        } else if (error.name === 'NotFoundError') {
          errorMsg = 'マイクが見つかりません。マイクが接続されているか確認してください。';
        } else {
          errorMsg = `録音エラー: ${error.message}`;
        }
      }
      
      if (onError) onError(errorMsg);
    }
  }, [recordingState, isSupported, onAudioData, onError, pcmToBase64]);

  const stopRecording = useCallback(() => {
    console.log('Stopping recording...');
    setRecordingState('idle');

    // AudioContext関連のクリーンアップ
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }

    if (analyserRef.current) {
      analyserRef.current.disconnect();
      analyserRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // MediaStreamの停止
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop();
      });
      streamRef.current = null;
    }

    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }

    console.log('Recording stopped');
  }, []);

  // クリーンアップ
  const cleanup = useCallback(() => {
    stopRecording();
  }, [stopRecording]);

  return {
    recordingState,
    startRecording,
    stopRecording,
    isSupported
  };
};
