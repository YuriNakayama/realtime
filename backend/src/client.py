import asyncio
import threading

import numpy as np
import pyaudio
import websockets

# WebSocketサーバーのURL
WS_SERVER_URL = "ws://localhost:8000/ws"

# オーディオ設定
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 100  # 1024

# PyAudioを初期化
p = pyaudio.PyAudio()

# ストリームを開く（マイク入力用）
input_stream = p.open(
    format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
)

# ストリームを開く（再生用）
output_stream = p.open(
    format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK
)

# グローバルフラグ
running = True


async def send_and_receive_audio(websocket):
    try:
        while running:
            # マイクから音声データを取得（バッファオーバーフロー対策）
            try:
                audio_data = input_stream.read(CHUNK, exception_on_overflow=False)
            except Exception as e:
                print(f"音声読み込みエラー: {e}")
                continue

            # WebSocketで音声データを送信
            await websocket.send(audio_data)

            # サーバーから処理済みの音声データを受信
            processed_audio = await websocket.recv()

            # 受信したデータを再生
            try:
                output_stream.write(processed_audio)
            except Exception as e:
                print(f"音声再生エラー: {e}")

    except Exception as e:
        print(f"エラー: {e}")


async def main():
    print(f"WebSocketサーバーに接続を試行中: {WS_SERVER_URL}")
    async with websockets.connect(WS_SERVER_URL) as websocket:
        print("WebSocket接続が成功しました")
        await send_and_receive_audio(websocket)


def cleanup_audio():
    """音声リソースのクリーンアップ"""
    try:
        if input_stream and not input_stream._stream is None:
            input_stream.stop_stream()
            input_stream.close()
    except Exception as e:
        print(f"入力ストリーム終了エラー: {e}")

    try:
        if output_stream and not output_stream._stream is None:
            output_stream.stop_stream()
            output_stream.close()
    except Exception as e:
        print(f"出力ストリーム終了エラー: {e}")

    try:
        p.terminate()
    except Exception as e:
        print(f"PyAudio終了エラー: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("プログラムが中断されました")
        running = False
    except Exception as e:
        print(f"メインエラー: {e}")
    finally:
        cleanup_audio()
