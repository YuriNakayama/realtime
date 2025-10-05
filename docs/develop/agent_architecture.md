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
from typing import Any
from dataclasses import dataclass
import numpy as np
import numpy.typing as npt

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
    
    def _initialize_client(self) -> RealtimeClient:
        """クライアントの初期化"""
        return RealtimeClient(
            name=self.config.name,
            instructions=self.instruction,
            api_key=self.config.api_key
        )
    
    async def process(
        self, 
        input_data: npt.NDArray[np.int16] | str
    ) -> npt.NDArray[np.int16] | str:
        """音声処理のメインメソッド"""
        # Orchestratorがルーティングを判断
        result = await self.orchestrator.invoke({
            "input": input_data,
            "agent_type": self.config.agent_type
        })
        
        # 該当するクライアントで処理
        if result.get("use_realtime"):
            return await self.realtime_client.send_request(input_data)
        return result.get("output", "")
    
    async def update_instructions(self, instructions: str) -> None:
        """プロンプトの動的更新"""
        self.instruction = instructions
        await self.realtime_client.update_instructions(instructions)


```

### 2. domainレイヤ

#### Orchestrator - マルチエージェント管理

```python
from abc import ABC, abstractmethod
from typing import Any, Protocol

class AbstractOrchestrator(ABC):
    """LangGraphベースのマルチエージェント管理インターフェース"""
    
    @abstractmethod
    async def invoke(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """LangGraphのグラフ実行"""
        pass


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
        self.session = None
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

class AbstractChatClient(ABC):
    """外部APIクライアントの基本インターフェース"""


class ChatClient(AbstractChatClient):
    """OpenAI Chat APIを使用したエージェント実装"""
```
