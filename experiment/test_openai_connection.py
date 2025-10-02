#!/usr/bin/env python3
"""
OpenAI Agents接続確認用の最小限のテストスクリプト
ログやエラーハンドリングは必要最低限とする
"""

import asyncio
import os
import time

from agents.realtime import RealtimeAgent, RealtimeModelConfig, RealtimeRunner
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
        await session.send_message("Hello, this is a connection test.")

        # 返答を待機して表示（3秒のタイムアウト付き）
        print("⏳ Waiting for response...")
        start_time = time.time()
        timeout = 3.0  # 3秒のタイムアウト

        try:
            async with asyncio.timeout(timeout):
                async for event in session:
                    logger.info(event)
                    if event.type == "response.done":
                        print("✅ Response received successfully")
                        break
                    elif event.type == "error":
                        print(f"❌ Error in response: {event.error}")
                        return False
                    elif hasattr(event, "text") and event.text:
                        print(f"💬 Agent response: {event.text}")
                    elif hasattr(event, "audio") and event.audio:
                        print(
                            f"🔊 Received audio data of length: {len(event.audio.data)}"
                        )
                    else:
                        print(f"❌ Unknown event: {event.type}")
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            print(f"⚠️ タイムアウト: {elapsed:.2f}秒経過しても応答が完了しませんでした")
            return False

        print(
            "\n🎉 All tests passed! OpenAI Agents connection and response are working correctly."
        )
        return True

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)
