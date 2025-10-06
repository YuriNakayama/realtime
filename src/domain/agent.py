import asyncio
import os

import numpy as np
import numpy.typing as npt
from agents.realtime import (
    RealtimeAgent,
    RealtimeModelConfig,
    RealtimePlaybackTracker,
    RealtimeRunner,
    RealtimeSession,
)
from dotenv import load_dotenv

from src.domain.log import get_logger

logger = get_logger(__name__)


class TestAgent:
    def __init__(self) -> None:
        pass

    async def __call__(self, audio: npt.NDArray[np.int16]) -> npt.NDArray[np.int16]:
        return audio * 2  # 例: 音量を2倍にする
