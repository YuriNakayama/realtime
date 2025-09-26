import { useRef, useCallback, useState } from 'react';
import type { PlaybackState } from '@/types/realtime';

interface UseAudioPlaybackProps {
  onPlaybackEnd?: () => void;
  onError?: (error: string) => void;
}

interface UseAudioPlaybackReturn {
  playbackState: PlaybackState;
  playAudio: (base64Audio: string) => Promise<void>;
  stopPlayback: () => void;
  isSupported: boolean;
}

export const useAudioPlayback = ({
  onPlaybackEnd,
  onError
}: UseAudioPlaybackProps): UseAudioPlaybackReturn => {
  const [playbackState, setPlaybackState] = useState<PlaybackState>('idle');
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceRef = useRef<AudioBufferSourceNode | null>(null);
  const audioBufferRef = useRef<AudioBuffer | null>(null);

  // Web Audio APIサポート確認
  const isSupported = typeof window !== 'undefined' && 
    ('AudioContext' in window || 'webkitAudioContext' in window);

  // Base64音声データをArrayBufferに変換
  const base64ToArrayBuffer = useCallback((base64: string): ArrayBuffer => {
    // Base64をバイナリ文字列にデコード
    const binaryString = atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    
    return bytes.buffer;
  }, []);

  // PCM16データをAudioBufferに変換
  const pcm16ToAudioBuffer = useCallback(async (arrayBuffer: ArrayBuffer): Promise<AudioBuffer> => {
    if (!audioContextRef.current) {
      throw new Error('AudioContext is not initialized');
    }

    // Int16Array として解釈（16kHz, モノラル, PCM16）
    const int16Array = new Int16Array(arrayBuffer);
    const sampleRate = 16000;
    const numberOfChannels = 1;
    const length = int16Array.length;

    // AudioBuffer作成
    const audioBuffer = audioContextRef.current.createBuffer(
      numberOfChannels,
      length,
      sampleRate
    );

    // Int16データ(-32768 to 32767)をFloat32データ(-1.0 to 1.0)に変換
    const channelData = audioBuffer.getChannelData(0);
    for (let i = 0; i < length; i++) {
      channelData[i] = int16Array[i] / 32768.0;
    }

    return audioBuffer;
  }, []);

  const playAudio = useCallback(async (base64Audio: string): Promise<void> => {
    if (!isSupported) {
      const errorMsg = 'このブラウザは音声再生をサポートしていません';
      console.error(errorMsg);
      if (onError) onError(errorMsg);
      return;
    }

    if (playbackState === 'playing') {
      // 既に再生中の場合は停止してから新しい音声を再生
      stopPlayback();
    }

    try {
      setPlaybackState('playing');

      // AudioContextを初期化（必要に応じて）
      if (!audioContextRef.current) {
        const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        audioContextRef.current = new AudioContextClass({
          sampleRate: 16000
        });
      }

      // AudioContextが停止している場合は再開
      if (audioContextRef.current.state === 'suspended') {
        await audioContextRef.current.resume();
      }

      // Base64データをArrayBufferに変換
      const arrayBuffer = base64ToArrayBuffer(base64Audio);
      
      // PCM16データをAudioBufferに変換
      const audioBuffer = await pcm16ToAudioBuffer(arrayBuffer);
      audioBufferRef.current = audioBuffer;

      // AudioBufferSourceNodeを作成
      const source = audioContextRef.current.createBufferSource();
      source.buffer = audioBuffer;
      sourceRef.current = source;

      // 再生終了時のコールバック
      source.onended = () => {
        console.log('Audio playback ended');
        setPlaybackState('idle');
        sourceRef.current = null;
        if (onPlaybackEnd) {
          onPlaybackEnd();
        }
      };

      // AudioContextのdestinationに接続して再生
      source.connect(audioContextRef.current.destination);
      source.start();

      console.log('Audio playback started');

    } catch (error) {
      console.error('Failed to play audio:', error);
      setPlaybackState('idle');
      
      let errorMsg = '音声の再生に失敗しました';
      if (error instanceof Error) {
        errorMsg = `再生エラー: ${error.message}`;
      }
      
      if (onError) onError(errorMsg);
    }
  }, [playbackState, isSupported, base64ToArrayBuffer, pcm16ToAudioBuffer, onError, onPlaybackEnd]);

  const stopPlayback = useCallback(() => {
    console.log('Stopping audio playback...');
    
    // 再生中のソースを停止
    if (sourceRef.current) {
      try {
        sourceRef.current.stop();
      } catch (error) {
        // 既に停止している場合はエラーを無視
        console.warn('Source already stopped:', error);
      }
      sourceRef.current = null;
    }

    setPlaybackState('idle');
    console.log('Audio playback stopped');
  }, []);

  // クリーンアップ
  const cleanup = useCallback(() => {
    stopPlayback();
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    audioBufferRef.current = null;
  }, [stopPlayback]);

  return {
    playbackState,
    playAudio,
    stopPlayback,
    isSupported
  };
};
