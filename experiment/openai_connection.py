#!/usr/bin/env python3
"""
OpenAI Agents接続確認用の最小限のテストスクリプト
ログやエラーハンドリングは必要最低限とする
"""

import asyncio
import os

from agents.realtime import RealtimeAgent, RealtimeModelConfig, RealtimeRunner
from agents.realtime.events import (
    RealtimeAgentEndEvent,
    RealtimeAgentStartEvent,
    RealtimeAudio,
    RealtimeAudioEnd,
    RealtimeHistoryAdded,
    RealtimeHistoryUpdated,
    RealtimeRawModelEvent,
)
from dotenv import load_dotenv

from experiment.log import get_logger


async def test_connection():
    logger = get_logger("connection_test", "logs/connection_test.log")
    if not load_dotenv():
        logger.warning("⚠️  .env file not found")

    api_key = os.getenv("OPENAI_API_KEY")

    try:
        agent = RealtimeAgent(
            name="Connection Test Agent",
            instructions="テストのために短く答えてください。",
        )
        runner = RealtimeRunner(agent)
        session = await runner.run(model_config=RealtimeModelConfig(api_key=api_key))
        await session.enter()
        await session.send_message("こんにちは！今は何時ですか？")

        timeout = 3.0  # 3秒のタイムアウト
        try:
            async with asyncio.timeout(timeout):
                async for event in session:
                    match event:
                        case RealtimeAgentStartEvent():
                            print("✅ Connection established successfully.")
                        case RealtimeAgentEndEvent():
                            print("✅ Agent finished responding.")
                        case RealtimeAudio():
                            print("🎤 Received audio chunk of size")
                        case RealtimeAudioEnd():
                            print("✅ Audio response ended.")
                        case RealtimeHistoryAdded():
                            print("📝 History added.")
                        case RealtimeHistoryUpdated():
                            print("📝 History updated.")
                        case RealtimeRawModelEvent():
                            print("🔄 Raw model event:")
                            logger.info(event)
                        case _:
                            print(f"Received event: {event}")
                            raise ValueError(f"Unexpected event type: {type(event)}")
        except asyncio.TimeoutError:
            return False

        print(
            "\n🎉 All tests passed! OpenAI Agents connection and response are working correctly."  # noqa: E501
        )
        return True

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)
