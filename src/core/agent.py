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

from src.core.log import get_logger

logger = get_logger(__name__)


class TestAgent:
    def __init__(self) -> None:
        pass

    async def __call__(self, audio: npt.NDArray[np.int16]) -> npt.NDArray[np.int16]:
        return audio * 2  # 例: 音量を2倍にする


class SimpleAgent:
    def __init__(self) -> None:
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
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": {
                    "type": "semantic_vad",
                    "interrupt_response": True,
                    "create_response": True,
                },
            },
            playback_tracker=RealtimePlaybackTracker(),
        )

        # セッションを初期化時に作成し、再利用する
        self.runner: RealtimeRunner | None = None
        self.session: RealtimeSession | None = None

    async def _initialize_session(self) -> None:
        """セッションを初期化する"""
        if self.runner is None:
            self.runner = RealtimeRunner(starting_agent=self.agent)
            self.session = await self.runner.run(model_config=self.config)
        elif self.session is None:
            self.session = await self.runner.run(model_config=self.config)

    async def __call__(self, audio: npt.NDArray[np.int16]) -> npt.NDArray[np.int16]:
        try:
            if len(audio) == 0:
                return audio

            # セッションが初期化されていない場合は初期化
            await self._initialize_session()

            # sessionがNoneでないことを確認
            if self.session is None:
                logger.error("セッションの初期化に失敗しました")
                return audio

            response_audio = np.array([], dtype=np.int16)

            # タイムアウト付きでセッション処理を実行
            try:
                async with asyncio.timeout(10.0):  # 10秒のタイムアウト
                    # numpy配列をbytesに変換
                    audio_bytes = audio.tobytes()
                    await self.session.send_audio(audio_bytes)

                    async for event in self.session:
                        logger.info(f"SimpleAgent: Received event - {event}")
                        if event.type == "audio":
                            if hasattr(event, "audio") and event.audio is not None:
                                # event.audioがbytes型の場合の処理
                                try:
                                    # まずbytes型として処理を試みる
                                    audio_array = np.frombuffer(
                                        event.audio,
                                        dtype=np.int16,  # type: ignore
                                    )
                                    response_audio = np.concatenate(
                                        (response_audio, audio_array)
                                    )
                                except (TypeError, AttributeError):
                                    # numpy配列の場合
                                    response_audio = np.concatenate(
                                        (response_audio, event.audio)  # type: ignore
                                    )
                        elif event.type == "audio_end":
                            break
                        elif event.type == "error":
                            logger.error(
                                f"SimpleAgent: RealtimeAgent error - {event.error}"
                            )
                            break

            except asyncio.TimeoutError:
                logger.warning("SimpleAgent: タイムアウトが発生しました")

            # レスポンスが空の場合は元の音声を返す
            if len(response_audio) == 0:
                return audio

            return response_audio

        except Exception as e:
            import traceback

            logger.error(f"SimpleAgent error: {e}")
            logger.error(f"SimpleAgent traceback: {traceback.format_exc()}")
            # エラー時は元の音声をそのまま返す
            return audio
