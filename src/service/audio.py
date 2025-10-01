import traceback

import numpy as np
from fastapi import WebSocket

from src.core.agent import SimpleAgent, TestAgent
from src.core.log import get_logger

logger = get_logger(__name__)


class AudioService:
    def __init__(self, websocket: WebSocket, agent: SimpleAgent) -> None:
        self.websocket = websocket
        self.agent = agent

    async def onopen(self) -> None:
        await self.websocket.accept()
        logger.info("WebSocket接続が確立されました")

    async def process_audio(self) -> None:
        try:
            while True:
                logger.info("AudioService: クライアントからのデータを待機中...")
                data = await self.websocket.receive_bytes()
                logger.info(f"AudioService: データ受信 - {len(data)} bytes")

                audio_data = np.frombuffer(data, dtype=np.int16)
                logger.info(
                    f"AudioService: 音声データ変換完了 - {len(audio_data)} samples"
                )

                logger.info("AudioService: エージェント処理開始...")
                processed_audio = await self.agent(audio_data)
                logger.info(
                    f"AudioService: エージェント処理完了 - {len(processed_audio)} samples"
                )

                await self.websocket.send_bytes(processed_audio.tobytes())
                logger.info("AudioService: 処理済み音声データを送信完了")
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            logger.info("WebSocket接続が閉じられました")

    async def __call__(self) -> None:
        await self.onopen()
        await self.process_audio()
