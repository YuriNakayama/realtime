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

class RealtimeService:
    """リアルタイム音声処理のサービスクラス"""
    def __init__(self, config: ServiceConfig, orchastrator: AbstractOrchestrator):
        self.config = config
        self.instruction: str = self.config.initial_instruction

        self.orchestrator = orchastrator
        self.realtime_agent = self._initialize_agent()
    
    def _initialize_agent(self) -> RealtimeAgent:
        """エージェントの初期化"""
        
    async def process(
        self, 
        input_data: npt.NDArray[np.int16]
    ) -> npt.NDArray[np.int16]:
        """音声処理のメインメソッド"""
        pass
    
    async def update_instructions(self, instructions: str) -> str:
        """プロンプトの動的更新"""
        pass

```

### 2. domainレイヤ

#### Orchestrator - マルチエージェント管理

```python
class AbstractOrchestrator(ABC):
    """マルチエージェント管理のインターフェース"""
    clients: dict[str, AbstractClient]
    
    @abstractmethod
    async def run(
        self, 
        input_data: str,
    ) -> str:
        """適切なエージェントへのルーティング"""
        pass


class AbstractAgent(ABC):
    """エージェントの基本インターフェース"""
    name: str
    
    @abstractmethod
    async def chat(
        self, 
        input_data: str,
    ) -> str:
        """エージェントのメイン処理"""
        pass

```

### 3. infrastructureレイヤ

#### OpenAIとの接続クライアント

```python
class AbstractClient(ABC):
    """外部APIクライアントの基本インターフェース"""
    
    @abstractmethod
    async def send_request(self, data: Any) -> Any:
        """外部APIへのリクエスト送信"""
        pass

class RealtimeClient:
    """OpenAI Realtime APIを使用したリアルタイム音声エージェント実装"""

class ChatClient:
    """OpenAI Chat APIを使用したエージェント実装"""
```
