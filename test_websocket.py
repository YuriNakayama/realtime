import asyncio

import numpy as np
import websockets


async def test_websocket():
    try:
        async with websockets.connect("ws://localhost:8000/realtime") as websocket:
            print("WebSocket接続成功")

            # 有効なPCM音声データを生成（1秒間、16kHz、16bit）
            sample_rate = 16000
            duration = 1.0  # 1秒
            frequency = 440  # A4音程（440Hz）

            # サイン波を生成
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            audio_data = np.sin(2 * np.pi * frequency * t)

            # int16形式に変換（-32768 から 32767 の範囲）
            audio_int16 = (audio_data * 32767).astype(np.int16)

            print(
                f"音声データ生成完了: {len(audio_int16)} samples, {audio_int16.dtype}"
            )

            # バイトデータとして送信
            await websocket.send(audio_int16.tobytes())
            print("音声データ送信完了")

            # 応答を待機（タイムアウト付き）
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            print(f"応答受信: {len(response)} bytes")

            # 応答を音声データとして解析
            response_audio = np.frombuffer(response, dtype=np.int16)
            print(f"応答音声データ: {len(response_audio)} samples")

    except asyncio.TimeoutError:
        print("タイムアウト: サーバーから応答がありません")
    except Exception as e:
        print(f"エラー: {e}")


asyncio.run(test_websocket())
