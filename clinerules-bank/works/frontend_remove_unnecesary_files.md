# フロントエンドリファクタリング - フォルダ構成提案

## ドメイン駆動設計（DDD）アプローチ

### 構成

```
frontend/src/
├── app/                           # Next.js App Router（現状維持）
│   ├── globals.css
│   ├── layout.tsx
│   ├── page.tsx
│   ├── api/
│   └── thank-you/
├── shared/                        # 共通・汎用
│   ├── components/                # 再利用可能なUIコンポーネント
│   │   ├── ui/                   # 基本UIコンポーネント（ボタン、モーダルなど）
│   │   └── layout/               # レイアウト関連
│   ├── hooks/                    # 汎用カスタムフック
│   ├── utils/                    # 汎用ユーティリティ
│   │   ├── api.ts
│   │   └── device.ts
│   ├── types/                    # 共通型定義
│   └── config/                   # アプリケーション設定
├── features/                      # 機能別ドメイン
│   ├── auth/                     # 認証機能
│   │   ├── components/
│   │   │   ├── AuthForm.tsx
│   │   │   ├── AuthPage.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx
│   │   ├── hooks/
│   │   ├── types/
│   │   │   └── auth.ts
│   │   └── utils/
│   ├── voice-chat/               # 音声チャット機能
│   │   ├── components/
│   │   │   ├── RealtimeStatus.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── VoiceChatInterface.tsx
│   │   ├── hooks/
│   │   │   └── useVoiceChat.ts
│   │   ├── config/
│   │   │   └── agents.ts
│   │   ├── types/
│   │   └── utils/
│   │       └── deviceChecker.ts
│   ├── session/                  # セッション管理
│   │   ├── components/
│   │   ├── contexts/
│   │   │   └── ChatSessionContext.tsx
│   │   ├── hooks/
│   │   ├── types/
│   │   │   └── database.ts
│   │   └── utils/
│   │       └── chatHistory.ts
│   └── summary/                  # サマリー機能
│       ├── components/
│       │   ├── HearingItemsPanel.tsx
│       │   ├── SummaryModal.tsx
│       │   ├── SummaryTextPanel.tsx
│       │   └── ThankYouPage.tsx
│       ├── hooks/
│       ├── types/
│       │   └── summary.ts
│       └── utils/
└── lib/                          # サードパーティライブラリ統合
    └── openai/
```

## 変更方針

### 1. フォルダ構造作成

#### 新規作成するフォルダ

```
frontend/src/shared/
frontend/src/shared/components/
frontend/src/shared/components/ui/
frontend/src/shared/components/layout/
frontend/src/shared/hooks/
frontend/src/shared/utils/
frontend/src/shared/types/
frontend/src/shared/config/
frontend/src/features/
frontend/src/features/auth/
frontend/src/features/auth/components/
frontend/src/features/auth/contexts/
frontend/src/features/auth/hooks/
frontend/src/features/auth/types/
frontend/src/features/auth/utils/
frontend/src/features/voice-chat/
frontend/src/features/voice-chat/components/
frontend/src/features/voice-chat/hooks/
frontend/src/features/voice-chat/config/
frontend/src/features/voice-chat/types/
frontend/src/features/voice-chat/utils/
frontend/src/features/session/
frontend/src/features/session/components/
frontend/src/features/session/contexts/
frontend/src/features/session/hooks/
frontend/src/features/session/types/
frontend/src/features/session/utils/
frontend/src/features/summary/
frontend/src/features/summary/components/
frontend/src/features/summary/hooks/
frontend/src/features/summary/types/
frontend/src/features/summary/utils/
frontend/src/lib/
```

### 2. ファイル移動計画

#### 認証機能 (features/auth/)

- `components/AuthForm.tsx` → `features/auth/components/AuthForm.tsx`
- `components/AuthPage.tsx` → `features/auth/components/AuthPage.tsx`
- `components/ProtectedRoute.tsx` → `shared/components/layout/ProtectedRoute.tsx`
- `contexts/AuthContext.tsx` → `features/auth/contexts/AuthContext.tsx`
- `types/auth.ts` → `features/auth/types/auth.ts`

#### 音声チャット機能 (features/voice-chat/)

- `components/RealtimeStatus.tsx` → `features/voice-chat/components/RealtimeStatus.tsx`
- `components/Sidebar.tsx` → `features/voice-chat/components/Sidebar.tsx`
- `hooks/useVoiceChat.ts` → `features/voice-chat/hooks/useVoiceChat.ts`
- `config/agents.ts` → `features/voice-chat/config/agents.ts`
- `utils/deviceChecker.ts` → `features/voice-chat/utils/deviceChecker.ts`

#### セッション管理 (features/session/)

- `contexts/ChatSessionContext.tsx` → `features/session/contexts/ChatSessionContext.tsx`
- `utils/chatHistory.ts` → `features/session/utils/chatHistory.ts`
- `types/database.ts` → `features/session/types/database.ts`

#### サマリー機能 (features/summary/)

- `components/summary/HearingItemsPanel.tsx` → `features/summary/components/HearingItemsPanel.tsx`
- `components/summary/SummaryModal.tsx` → `features/summary/components/SummaryModal.tsx`
- `components/summary/SummaryTextPanel.tsx` → `features/summary/components/SummaryTextPanel.tsx`
- `components/ThankYouPage.tsx` → `features/summary/components/ThankYouPage.tsx`
- `types/summary.ts` → `features/summary/types/summary.ts`

#### 共有リソース (shared/)

- `utils/apiClient.ts` → `shared/utils/apiClient.ts`
- `utils/client.ts` → `lib/client.ts`
- `config/environment.ts` → `shared/config/environment.ts`

#### その他

- `components/ToolExecutionHistory.tsx` → `features/voice-chat/components/ToolExecutionHistory.tsx`

### 3. インポートパス更新

#### 各ファイルで更新が必要なインポートパス

- `app/page.tsx` - 全コンポーネント、フック、コンテキストのインポートパス更新
- 移動されたコンポーネント内の相対インポートパス更新
- TypeScript設定でのパスマッピング追加検討

### 4. 削除するフォルダ（空になった後）

```
frontend/src/components/
frontend/src/contexts/
frontend/src/hooks/
frontend/src/types/
frontend/src/utils/
frontend/src/config/
```
