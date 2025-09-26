# APIのリファクタリング

## apiを使用中のファイル

- frontend/src/contexts/authContext.tsx
- frontend/src/utils/authClient.ts
- frontend/src/utils/sessionApi.ts
- frontend/src/utils/summaryApi.ts

## frontendで使用中のAPI

認証

- ${BACKEND_URL}/auth/session
- ${BACKEND_URL}/auth/signup
- ${BACKEND_URL}/auth/login
- ${BACKEND_URL}/auth/logout
- ${BACKEND_URL}/auth/confirm-signup

セッション・チャット関連

- ${BACKEND_URL}/sessions
- ${BACKEND_URL}/sessions/${data.id}
- ${BACKEND_URL}/sessions/create
- ${BACKEND_URL}/sessions/list
- ${BACKEND_URL}/sessions/${sessionId}/messages
- ${BACKEND_URL}/sessions/${sessionId}

リアルタイムチャット関連

- ${BACKEND_URL}/sessions/${sessionId}/realtime/status
- ${BACKEND_URL}/sessions/${sessionId}/realtime/connect
- ${BACKEND_URL}/sessions/${sessionId}/realtime/disconnect

要約関連

- ${BACKEND_URL}/summary/generate
- ${BACKEND_URL}/summary/save
- ${BACKEND_URL}/summary?${queryParams.toString()}
- ${BACKEND_URL}/summary/${summaryId}
