import numpy as np
import uvicorn
import websockets
from fastapi import FastAPI, WebSocket


async def process_audio(websocket, path):
    print("接続中")

    try:
        async for message in websocket:
            audio_data = np.frombuffer(message, dtype=np.int16)
            print(f"受信した音声データの長さ: {len(audio_data)}")
            # ここで音声データを処理するコードを追加できます
            processed_data = audio_data * 2  # 例: 音量を2倍にする
            await websocket.send(processed_data.tobytes())
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        print("接続終了")


app = FastAPI()


@app.get("/")
async def get():
    return {"message": "Hello, World!"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket接続が確立されました")
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_data = np.frombuffer(data, dtype=np.int16)
            print(f"受信した音声データの長さ: {len(audio_data)}")
            processed_audio = audio_data * 2  # 例: 音量を2倍にする
            await websocket.send_bytes(processed_audio.tobytes())
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        print("WebSocket接続が閉じられました")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")
