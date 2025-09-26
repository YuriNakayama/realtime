"""
音声データ処理ユーティリティ
"""

import base64
import logging
from typing import List

import numpy as np
from scipy import signal

from .models import AudioFormat

logger = logging.getLogger(__name__)


class AudioProcessor:
    """音声データの変換と検証を行うクラス"""

    @staticmethod
    def encode_audio(
        audio_bytes: bytes, audio_format: AudioFormat = AudioFormat.PCM16
    ) -> str:
        """音声データをBase64エンコードする

        Args:
            audio_bytes: 音声データ（bytes）
            audio_format: 音声フォーマット

        Returns:
            Base64エンコードされた音声データ
        """
        try:
            if audio_format == AudioFormat.PCM16:
                # PCM16の場合はそのままBase64エンコード
                return base64.b64encode(audio_bytes).decode("utf-8")
            else:
                # 他のフォーマットも同様に処理（今後の拡張用）
                return base64.b64encode(audio_bytes).decode("utf-8")
        except Exception as e:
            logger.error(f"音声エンコードエラー: {e}")
            raise

    @staticmethod
    def decode_audio(
        audio_base64: str, audio_format: AudioFormat = AudioFormat.PCM16
    ) -> bytes:
        """Base64エンコードされた音声データをデコードする

        Args:
            audio_base64: Base64エンコードされた音声データ
            audio_format: 音声フォーマット

        Returns:
            デコードされた音声データ（bytes）
        """
        try:
            return base64.b64decode(audio_base64)
        except Exception as e:
            logger.error(f"音声デコードエラー: {e}")
            raise

    @staticmethod
    def validate_audio_format(
        audio_data: bytes,
        expected_format: AudioFormat = AudioFormat.PCM16,
        expected_sample_rate: int = 24000,
        expected_channels: int = 1,
    ) -> bool:
        """音声フォーマットを検証する

        Args:
            audio_data: 音声データ
            expected_format: 期待される音声フォーマット
            expected_sample_rate: 期待されるサンプルレート
            expected_channels: 期待されるチャンネル数

        Returns:
            検証結果
        """
        try:
            if expected_format == AudioFormat.PCM16:
                # PCM16の場合、2バイトごとに1サンプル
                if len(audio_data) % 2 != 0:
                    logger.warning("PCM16データのバイト数が奇数です")
                    return False

                # サンプル数を計算
                samples = len(audio_data) // 2 // expected_channels

                # 最小限のサンプル数チェック
                if samples < 1:
                    logger.warning("音声データが短すぎます")
                    return False

                return True
            else:
                # 他のフォーマットの検証（今後の拡張用）
                logger.warning(f"未対応の音声フォーマット: {expected_format}")
                return True

        except Exception as e:
            logger.error(f"音声フォーマット検証エラー: {e}")
            return False

    @staticmethod
    def convert_sample_rate(
        audio_data: bytes, from_rate: int, to_rate: int, channels: int = 1
    ) -> bytes:
        """サンプルレートを変換する

        Args:
            audio_data: 音声データ
            from_rate: 元のサンプルレート
            to_rate: 変換先のサンプルレート
            channels: チャンネル数

        Returns:
            変換された音声データ
        """
        try:
            if from_rate == to_rate:
                return audio_data

            # バイト配列をint16配列に変換
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # チャンネル数に応じて整形
            if channels > 1:
                audio_array = audio_array.reshape(-1, channels)

            # サンプルレート変換
            num_samples = int(len(audio_array) * to_rate / from_rate)
            resampled = signal.resample(audio_array, num_samples)

            # int16に変換してバイト配列に戻す
            resampled_int16 = resampled.astype(np.int16)

            return resampled_int16.tobytes()

        except Exception as e:
            logger.error(f"サンプルレート変換エラー: {e}")
            raise

    @staticmethod
    def chunk_audio(audio_data: bytes, chunk_size: int = 1024) -> List[bytes]:
        """音声データをチャンクに分割する

        Args:
            audio_data: 音声データ
            chunk_size: チャンクサイズ（バイト単位）

        Returns:
            分割された音声データのリスト
        """
        try:
            chunks = []
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i : i + chunk_size]
                chunks.append(chunk)
            return chunks

        except Exception as e:
            logger.error(f"音声チャンク分割エラー: {e}")
            raise

    @staticmethod
    def normalize_audio(audio_data: bytes, target_level: float = 0.8) -> bytes:
        """音声データを正規化する

        Args:
            audio_data: 音声データ
            target_level: ターゲットレベル（0.0-1.0）

        Returns:
            正規化された音声データ
        """
        try:
            # バイト配列をfloat配列に変換
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)

            # 正規化
            max_val = np.max(np.abs(audio_array))
            if max_val > 0:
                # ターゲットレベルに調整
                normalized = audio_array * (target_level * 32767.0 / max_val)
                # int16範囲にクリップ
                normalized = np.clip(normalized, -32768, 32767)
            else:
                normalized = audio_array

            return normalized.astype(np.int16).tobytes()

        except Exception as e:
            logger.error(f"音声正規化エラー: {e}")
            raise

    @staticmethod
    def detect_silence(
        audio_data: bytes,
        threshold: float = 0.01,
        min_silence_duration_ms: int = 500,
        sample_rate: int = 24000,
    ) -> List[tuple[int, int]]:
        """無音区間を検出する

        Args:
            audio_data: 音声データ
            threshold: 無音判定の閾値（0.0-1.0）
            min_silence_duration_ms: 最小無音継続時間（ミリ秒）
            sample_rate: サンプルレート

        Returns:
            無音区間のリスト（開始位置、終了位置のタプル）
        """
        try:
            # バイト配列をfloat配列に変換
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            audio_array = audio_array / 32768.0  # -1.0 to 1.0に正規化

            # 無音判定
            is_silence = np.abs(audio_array) < threshold

            # 最小継続時間をサンプル数に変換
            min_silence_samples = int(min_silence_duration_ms * sample_rate / 1000)

            silence_regions = []
            silence_start = None

            for i, silent in enumerate(is_silence):
                if silent and silence_start is None:
                    silence_start = i
                elif not silent and silence_start is not None:
                    if i - silence_start >= min_silence_samples:
                        silence_regions.append((silence_start, i))
                    silence_start = None

            # 最後が無音で終わる場合
            if silence_start is not None:
                if len(is_silence) - silence_start >= min_silence_samples:
                    silence_regions.append((silence_start, len(is_silence)))

            return silence_regions

        except Exception as e:
            logger.error(f"無音検出エラー: {e}")
            return []
