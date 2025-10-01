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
                data = await self.websocket.receive_bytes()
                audio_data = np.frombuffer(data, dtype=np.int16)
                processed_audio = await self.agent(audio_data)
                await self.websocket.send_bytes(processed_audio.tobytes())
        except Exception:
            logger.error(traceback.format_exc())
        finally:
            logger.info("WebSocket接続が閉じられました")

    async def __call__(self) -> None:
        await self.onopen()
        await self.process_audio()
