import asyncio
from dataclasses import dataclass

import websockets
from pyaudio import PyAudio, paInt16

from src.core.log import get_logger

logger = get_logger(__name__)


async def send_and_receive_audio(websocket, input_stream, output_stream, chunk) -> None:
    try:
        while True:
            # マイクから音声データを取得（バッファオーバーフロー対策）
            audio_data = input_stream.read(chunk)

            # WebSocketで音声データを送信
            await websocket.send(audio_data)

            # サーバーから処理済みの音声データを受信
            processed_audio = await websocket.recv()

            # 受信したデータを再生
            output_stream.write(processed_audio)

    except Exception as e:
        logger.error(f"エラー: {e}")


@dataclass
class AudioConfig:
    format: int = paInt16
    channels: int = 1
    rate: int = 16000
    chunk: int = 1000  # 1024


async def main(url: str) -> None:
    config = AudioConfig()
    p = PyAudio()
    # ストリームを開く（マイク入力用）
    input_stream = p.open(
        format=config.format,
        channels=config.channels,
        rate=config.rate,
        input=True,
        frames_per_buffer=config.chunk,
    )

    # ストリームを開く（再生用）
    output_stream = p.open(
        format=config.format,
        channels=config.channels,
        rate=config.rate,
        output=True,
        frames_per_buffer=config.chunk,
    )

    logger.info(f"WebSocketサーバーに接続を試行中: {url}")
    async with websockets.connect(url) as websocket:
        logger.info("WebSocket接続が成功しました")
        await send_and_receive_audio(
            websocket,
            input_stream=input_stream,
            output_stream=output_stream,
            chunk=config.chunk,
        )


if __name__ == "__main__":
    # WebSocketサーバーのURL
    WS_SERVER_URL = "ws://localhost:8000/realtime"

    try:
        asyncio.run(main(WS_SERVER_URL))
    except Exception as e:
        logger.error(e)
