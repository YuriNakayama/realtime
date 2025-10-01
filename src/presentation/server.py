import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket
from openai import audio

from src.core.agent import SimpleAgent, TestAgent
from src.service.audio import AudioService

app = FastAPI()


@app.get("/")
async def get():
    return {"message": "Hello, World!"}


@app.websocket("/realtime")
async def websocket_endpoint(websocket: WebSocket) -> None:
    audio_service = AudioService(websocket, agent=SimpleAgent())
    await audio_service()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")
