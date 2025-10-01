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


class TestAgent:
    def __init__(self):
        pass

    async def __call__(self, audio: npt.NDArray[np.int16]) -> npt.NDArray[np.int16]:
        return audio * 2  # 例: 音量を2倍にする


class SimpleAgent:
    def __init__(self):
        if not load_dotenv():
            print("No .env file found")

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("No OPENAI_API_KEY found in environment variables")

        self.agent = RealtimeAgent(
            name="Test Agent", instructions="すべての語尾に!!!をつけて話してください。"
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
        runner = RealtimeRunner(self.agent)
        async with await runner.run(model_config=self.config) as session:
            await session.send_audio(audio)
            response_audio = np.array([], dtype=np.int16)
            async for event in session:
                if isinstance(event, RealtimeSession.AudioEvent):
                    response_audio = np.concatenate((response_audio, event.audio))
            return response_audio
