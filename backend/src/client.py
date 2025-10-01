import asyncio
import threading

import numpy as np
import pyaudio
import websockets

# WebSocketサーバーのURL
WS_SERVER_URL = "ws://localhost:8000"

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
            # マイクから音声データを取得
            audio_data = input_stream.read(CHUNK)

            # WebSocketで音声データを送信
            await websocket.send(audio_data)

            # サーバーから処理済みの音声データを受信
            processed_audio = await websocket.recv()

            # 受信したデータを再生
            output_stream.write(processed_audio)

    except Exception as e:
        print(f"エラー: {e}")


async def main():
    async with websockets.connect(WS_SERVER_URL) as websocket:
        await send_and_receive_audio(websocket)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        running = False
    finally:
        # ストリームとPyAudioを閉じる
        input_stream.stop_stream()
        input_stream.close()
        output_stream.stop_stream()
        output_stream.close()
        p.terminate()
