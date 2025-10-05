# Realtime Agent アーキテクチャ設計書

## 概要

本ドキュメントは、multi agent化、Realtime Agentのプロンプト動的更新を見越したRealtime Agentシステムのアーキテクチャ設計を定義します。

## 現状分析

### 既存実装の構成

- **SimpleAgent**: OpenAI Realtime APIを使用した基本的なエージェント実装
- **AudioService**: WebSocket経由での音声処理サービス
- **FastAPI Server**: WebSocketエンドポイントの提供

## アーキテクチャ設計

### 1. serviceレイヤ

```python
# src/core/interfaces.py
from typing import Any, Callable, AsyncIterator
from dataclasses import dataclass
import numpy as np
import numpy.typing as npt
import asyncio

@dataclass
class ServiceConfig:
    """エージェントの設定を管理"""
    name: str
    initial_instruction: str
    model_settings: dict[str, Any]
    agent_type: str = "realtime"  # realtime/chat
    api_key: str | None = None  # APIキーの管理


class RealtimeService:
    """リアルタイム音声処理のサービスクラス"""
    def __init__(self, config: ServiceConfig, orchestrator: AbstractOrchestrator):
        self.config = config
        self.instruction: str = self.config.initial_instruction
        self.orchestrator = orchestrator
        self.realtime_client = self._initialize_client()
        self.orchestrator.set_callback(self._on_orchestrator_complete)
    
    def _initialize_client(self) -> RealtimeClient:
        """クライアントの初期化"""
        return RealtimeClient(
            name=self.config.name,
            instructions=self.instruction,
            api_key=self.config.api_key
        )
    
    async def process(
        self, 
        input_data: npt.NDArray[np.int16]
    ) -> AsyncIterator[npt.NDArray[np.int16]]:
        """音声処理のメインメソッド（非同期ストリーム）"""
        # Orchestratorを非同期で起動（完了を待たない）
        asyncio.create_task(self.orchestrator.invoke({
            "input": input_data,
            "agent_type": self.config.agent_type
        }))
        
        # すぐにRealtimeクライアントでの処理を開始
        async for response in self.realtime_client.send_request(input_data):
            yield response
    
    async def _on_orchestrator_complete(self, result: dict[str, Any]) -> None:
        """Orchestrator完了時のコールバック"""
        if new_instruction := result.get("instruction_update"):
            await self.update_instructions(new_instruction)
    
    async def update_instructions(self, instructions: str) -> None:
        """プロンプトの動的更新"""
        self.instruction = instructions
        await self.realtime_client.update_instructions(instructions)


```

### 2. domainレイヤ

#### Orchestrator - マルチエージェント管理

```python
from abc import ABC, abstractmethod
from typing import Any, Protocol, Callable

class AbstractOrchestrator(ABC):
    """LangGraphベースのマルチエージェント管理インターフェース"""
    
    def __init__(self):
        self._callback: Callable[[dict[str, Any]], None] | None = None
    
    @abstractmethod
    async def invoke(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """LangGraphのグラフ実行"""
        pass
    
    def set_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """完了時のコールバック設定"""
        self._callback = callback
    
    async def _notify_completion(self, result: dict[str, Any]) -> None:
        """完了通知"""
        if self._callback:
            await self._callback(result)


```

### 3. infrastructureレイヤ

#### OpenAIとの接続クライアント

```python
class RealtimeClient:
    """OpenAI Realtime APIを使用したリアルタイム音声エージェント実装"""
    
    def __init__(self, name: str, instructions: str, api_key: str | None):
        self.agent = RealtimeAgent(
            name=name,
            instructions=instructions
        )
        self.runner = RealtimeRunner(self.agent)
        self.session: RealtimeSession | None = None
        self.api_key = api_key
    
    async def connect(self) -> None:
        """接続処理"""
        model_config = RealtimeModelConfig(api_key=self.api_key)
        self.session = await self.runner.run(model_config=model_config)
        await self.session.enter()
    
    async def disconnect(self) -> None:
        """切断処理"""
        if self.session:
            # セッションのクリーンアップ
            self.session = None
    
    async def send_request(self, data: str | npt.NDArray[np.int16]) -> AsyncIterator[Any]:
        """メッセージ送信とイベントストリーム処理"""
        if not self.session:
            await self.connect()
        
        # テキストメッセージの場合
        if isinstance(data, str):
            await self.session.send_message(data)
        
        # イベントストリームの処理
        async for event in self.session:
            yield event
    
    async def update_instructions(self, instructions: str) -> None:
        """インストラクションの更新"""
        self.agent.instructions = instructions
        # 必要に応じてセッションの再構築
        if self.session:
            await self.disconnect()
            await self.connect()


class AbstractChatClient(ABC):
    """外部APIクライアントの基本インターフェース"""
    
    @abstractmethod
    async def chat(self, message: str) -> str:
        """メッセージ送信の抽象メソッド"""
        pass


class OpenAIChatClient(AbstractChatClient):
    """OpenAI Chat APIを使用したエージェント実装"""
    
    async def chat(self, message: str) -> str:
        """メッセージ送信の実装"""
        # 具象実装は後で行う
        pass
```
