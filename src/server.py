from openai import audio
import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket
from .audio_service import AudioService
from .agent import TestAgent



app = FastAPI()


@app.get("/")
async def get():
    return {"message": "Hello, World!"}


@app.websocket("/realtime")
async def websocket_endpoint(websocket: WebSocket) -> None:
    audio_service = AudioService(websocket, agent=TestAgent())
    await audio_service()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")
