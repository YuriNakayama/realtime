# Implementation Plan

## [Overview]

フロントエンドのHydrationエラーを修正し、音声コントロールを接続/切断ボタンのみに簡素化する。

現在のVoiceChatコンポーネントはNext.js 15のSSRでHydrationエラーが発生しており、複数の音声制御ボタンによる複雑な状態管理が問題となっている。この実装では、サーバーサイドレンダリング時の動的コンテンツ表示を修正し、WebSocket接続の制御を「接続」「切断」ボタンのみに簡素化することで、Hydrationエラーを解消し、ユーザビリティを向上させる。

## [Types]

既存の型定義は維持し、新しいUI状態管理用の型を追加する。

```typescript
// 接続状態を管理する型（既存のConnectionStatusを活用）
type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'disconnecting';

// 簡素化されたボタンの状態を管理する型
interface ButtonState {
  connect: {
    disabled: boolean;
    text: string;
  };
  disconnect: {
    disabled: boolean;
    text: string;
  };
}

// サーバーサイドレンダリング対応の型
interface SSRSafeState {
  isClient: boolean;
  isSupported: boolean;
}
```

## [Files]

既存ファイルの修正のみで、新しいファイルの作成は不要。

修正対象ファイル：

- `frontend/src/components/VoiceChat.tsx`: Hydrationエラー修正、UIボタンの簡素化、接続制御ロジックの修正
- `frontend/src/hooks/useWebSocket.ts`: autoConnect動作の調整（必要に応じて）
- `frontend/src/hooks/useAudioRecording.ts`: 自動録音開始の対応（必要に応じて）

## [Functions]

Hydrationエラーを回避し、WebSocket接続制御を単純化する。

新しい関数：

- `handleConnect()`: WebSocket接続と音声録音の自動開始
- `handleDisconnect()`: WebSocket切断と音声処理の停止
- `getButtonState(connectionState)`: 現在の接続状態に基づくボタン状態の取得
- `useSSRSafe()`: サーバーサイドレンダリング対応のカスタムフック

削除する関数：

- `handleStartRecording()`: 個別の録音開始制御
- `handleStopRecording()`: 個別の録音停止制御
- `handleInterrupt()`: 会話中断制御
- 録音/再生状態に基づく動的UI表示関数

修正する関数：

- `handleConnectionToggle()`: 接続/切断の統合制御に変更
- WebSocket接続時の自動音声録音開始処理
- SSRでの条件分岐を削除してHydrationエラーを回避

## [Classes]

クラスベースの実装は使用しておらず、関数コンポーネントとフックベースのため修正不要。

既存のReactコンポーネントとカスタムフックの構造は維持し、内部実装のみを修正する。

## [Dependencies]

既存の依存関係を維持し、新しい依存関係の追加は不要。

現在使用中のパッケージ：

- React 19
- Next.js 15.4+
- TypeScript
- WebSocket API (ブラウザネイティブ)
- Lucide React (アイコン)

## [Testing]

既存のテスト構造に合わせて手動テストとブラウザでの動作確認を実施。

テスト項目：

- Hydrationエラーの解消確認
- 接続ボタンクリック時のWebSocket接続確立と自動音声録音開始
- 切断ボタンクリック時の適切な切断処理と音声処理停止
- ボタン状態の適切な更新
- エラーハンドリングの動作確認
- サーバーサイドレンダリングとクライアントサイドの一貫性

## [Implementation Order]

段階的な実装でHydrationエラーとUIエラーリスクを最小化。

1. VoiceChat.tsxのHydrationエラー修正（条件分岐によるSSR/CSR差異の解消）
2. 不要なボタンとUI要素の削除（録音/停止、中断ボタン、動的インジケーター）
3. 接続/切断ボタンの統合イベントハンドラー実装
4. WebSocket接続時の自動音声録音開始実装
5. エラーハンドリングの改善
6. ボタン状態管理の実装
7. 動作テストと最終調整
