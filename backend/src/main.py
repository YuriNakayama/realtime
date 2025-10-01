import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket


async def process_audio(websocket: WebSocket) -> None:
    await websocket.accept()
    print("WebSocket接続が確立されました")
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_data = np.frombuffer(data, dtype=np.int16)
            processed_audio = audio_data * 2  # 例: 音量を2倍にする
            await websocket.send_bytes(processed_audio.tobytes())
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        print("WebSocket接続が閉じられました")


app = FastAPI()


@app.get("/")
async def get():
    return {"message": "Hello, World!"}


@app.websocket("/realtime")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await process_audio(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")
