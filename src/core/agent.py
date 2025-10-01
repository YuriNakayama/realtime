import os

import numpy as np
import numpy.typing as npt
from agents.realtime import (
    RealtimeAgent,
    RealtimeModelConfig,
    RealtimePlaybackTracker,
    RealtimeRunner,
)
from dotenv import load_dotenv

from src.core.log import get_logger

logger = get_logger(__name__)


class TestAgent:
    def __init__(self):
        pass

    async def __call__(self, audio: npt.NDArray[np.int16]) -> npt.NDArray[np.int16]:
        return audio * 2  # 例: 音量を2倍にする


class SimpleAgent:
    def __init__(self):
        if not load_dotenv():
            logger.error("No .env file found")

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("No OPENAI_API_KEY found in environment variables")

        self.agent = RealtimeAgent(
            name="Assistant",
            instructions="すべての語尾に「わ〜」をつけて話してください。",  # noqa: E501
        )

        self.config = RealtimeModelConfig(
            api_key=api_key,
            initial_model_settings={
                "input_audio_format": "g711_ulaw",
                "output_audio_format": "g711_ulaw",
                "turn_detection": {
                    "type": "semantic_vad",
                    "interrupt_response": True,
                    "create_response": True,
                },
            },
            playback_tracker=RealtimePlaybackTracker(),
        )

    async def __call__(self, audio: npt.NDArray[np.int16]) -> npt.NDArray[np.int16]:
        try:
            runner = RealtimeRunner(
                starting_agent=self.agent,
            )

            session = await runner.run(model_config=self.config)
            response_audio = np.array([], dtype=np.int16)

            async with session:
                await session.send_audio(audio)

                async for event in session:
                    if event.type == "audio":
                        if hasattr(event, "audio") and event.audio is not None:
                            response_audio = np.concatenate(
                                (response_audio, event.audio)
                            )
                    elif event.type == "audio_end":
                        break
                    elif event.type == "error":
                        logger.error(f"RealtimeAgent error: {event.error}")
                        break

            return response_audio

        except Exception as e:
            logger.error(f"SimpleAgent error: {e}")
            # エラー時は元の音声をそのまま返す
            return audio
