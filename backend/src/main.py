import logging
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import config
from .models import RealtimeMessageType, SessionConfig
from .session_manager import session_manager

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OpenAI Realtime API Server",
    version="1.0.0",
    debug=True,
    log_level="info",
    reload=True,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定検証
config.validate_config()


@app.get("/", response_class=JSONResponse)
async def index_page() -> dict[str, str]:
    return {"message": "OpenAI Realtime API Server is running!"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket) -> None:
    """WebSocket endpoint for realtime voice chat with OpenAI."""
    await websocket.accept()

    # セッション作成
    client_id = str(uuid.uuid4())
    session = session_manager.create_session(
        client_id=client_id, websocket=websocket, config=SessionConfig()
    )

    logger.info(f"新しいWebSocket接続: session_id={session.session_id}")

    # 接続確立通知
    await websocket.send_json(
        {
            "type": RealtimeMessageType.CONNECTION_ESTABLISHED.value,
            "sessionId": session.session_id,
        }
    )

    try:
        # WebSocketハンドラーを呼び出し（後で実装）
        from .websocket_handler import handle_websocket_connection

        await handle_websocket_connection(websocket, session)

    except WebSocketDisconnect:
        logger.info(f"WebSocket切断: session_id={session.session_id}")
    except Exception as e:
        logger.error(f"WebSocketエラー: {e}")
        await websocket.send_json(
            {
                "type": RealtimeMessageType.ERROR.value,
                "message": str(e),
                "code": "WEBSOCKET_ERROR",
            }
        )
    finally:
        # セッションクリーンアップ
        session_manager.remove_session(session.session_id)
        logger.info(f"セッション削除: session_id={session.session_id}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.HOST, port=config.PORT)
