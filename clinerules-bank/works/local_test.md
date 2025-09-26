# Frontend環境変数管理変更 - ローカル環境検証

## 検証の目的

frontend環境変数管理の変更（environment.ts集約化）がローカル開発環境で正常に動作することを確認する。

## 実施した変更の概要

### 変更内容

1. **環境変数ファイル整備**
   - `.env.example`: 既存設定の確認（NEXT_PUBLIC_BACKEND_URL、NEXT_PUBLIC_APP_NAME）
   - `.env.local`: ローカル開発用設定を新規作成

2. **環境変数集約管理の実装**
   - `src/config/environment.ts`: 型安全な環境変数アクセスを提供

3. **既存コードの更新**
   - 5つのファイルで`process.env`直接参照を`environment.ts`経由に変更
   - `src/utils/auth/apiClient.ts`
   - `src/contexts/AuthContext.tsx`
   - `src/hooks/useObserver.ts`
   - `src/services/hearingItemManager.ts`
   - `src/services/observerAI.ts`

## 前提条件

- [x] Node.js 18以上がインストールされている
- [x] npm または yarn がインストールされている
- [x] backendサーバーが localhost:8000 で稼働している（または稼働可能な状態）
- [x] VSCode または他のIDEでプロジェクトが開かれている

## 検証手順

### 1. 環境変数ファイル確認

#### 1.1 作成されたファイルの確認

```bash
# frontendディレクトリに移動
cd frontend

# 環境変数ファイルが作成されていることを確認
ls -la .env*
```

**期待される結果:**

```
.env.example  # 既存ファイル
.env.local    # 新規作成ファイル
```

#### 1.2 .env.localの内容確認

```bash
cat .env.local
```

**期待される内容:**

```
# ローカル開発用の設定
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AI相談窓口
```

#### 1.3 .env.exampleの内容確認

```bash
cat .env.example
```

**期待される内容:**

```
# Backend API Configuration (Required)
NEXT_PUBLIC_BACKEND_URL=https://your-backend-api-url

# Optional: App Configuration
NEXT_PUBLIC_APP_NAME=AI相談窓口
```

### 2. environment.ts実装確認

#### 2.1 ファイル存在確認

```bash
ls -la src/config/environment.ts
```

#### 2.2 ファイル内容確認

```bash
cat src/config/environment.ts
```

**期待される内容:**

```typescript
/**
 * 環境変数の集約管理
 * 型安全な環境変数アクセスを提供
 */

export const environment = {
  // APIベースURL
  apiBaseUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
  
  // アプリケーション名
  appName: process.env.NEXT_PUBLIC_APP_NAME || 'AI相談窓口',
} as const;

// 型定義
export type Environment = typeof environment;
```

### 3. 既存コード変更確認

#### 3.1 各ファイルのimport文確認

```bash
# 各ファイルでenvironment.tsがimportされているか確認
grep -n "import.*environment" src/utils/auth/apiClient.ts
grep -n "import.*environment" src/contexts/AuthContext.tsx  
grep -n "import.*environment" src/hooks/useObserver.ts
grep -n "import.*environment" src/services/hearingItemManager.ts
grep -n "import.*environment" src/services/observerAI.ts
```

#### 3.2 process.env直接参照が削除されているか確認

```bash
# process.envの直接参照が残っていないか確認
grep -r "process\.env\.NEXT_PUBLIC" src/ --exclude-dir=node_modules || echo "✅ 直接参照は削除済み"
```

### 4. TypeScriptコンパイル確認

#### 4.1 依存関係のインストール

```bash
# 必要に応じて依存関係を最新化
npm install
```

#### 4.2 TypeScript型チェック

```bash
# TypeScriptコンパイルエラーがないか確認
npx tsc --noEmit
```

**期待される結果:** エラーなしでコンパイル完了

#### 4.3 Lintチェック

```bash
# ESLintによるコード品質チェック
npm run lint
```

**期待される結果:** エラーなしまたは既存エラーのみ

### 5. ビルド確認

#### 5.1 Next.jsビルド

```bash
# 本番ビルドが成功することを確認
npm run build
```

**期待される結果:**

- ✅ ビルド成功
- environment.tsが正しく参照されている
- 環境変数が適切に読み込まれている

#### 5.2 ビルド結果の確認

```bash
# ビルド結果を確認
ls -la .next/
```

### 6. 開発サーバー起動確認

#### 6.1 開発サーバー起動

```bash
# 開発サーバーを起動
npm run dev
```

#### 6.2 起動ログ確認

**期待されるログ:**

```
✓ Ready in 2.1s
✓ Local:    http://localhost:3000
✓ Network:  use --host to expose
```

#### 6.3 ブラウザでアクセス

- ブラウザで `http://localhost:3000` にアクセス
- ページが正常に読み込まれることを確認

### 7. 環境変数動作確認

#### 7.1 ブラウザ開発者ツールでの確認

1. ブラウザで開発者ツールを開く（F12）
2. Consoleタブを選択
3. 以下のコードを実行:

```javascript
// environment.tsから取得される値を確認（直接はアクセスできないため、Network タブで確認）
console.log('Current location:', window.location.origin);
```

#### 7.2 Network タブでAPI呼び出し確認

1. 開発者ツールのNetworkタブを開く
2. アプリケーション上でAPIを使用する操作を実行（ログイン試行など）
3. API呼び出しのURLが `http://localhost:8000` で始まっていることを確認

### 8. 機能動作確認

#### 8.1 認証機能テスト

**前提:** backendサーバーが localhost:8000 で稼働している

1. **ログイン画面確認**
   - [ ] ログイン画面が表示される
   - [ ] フォームが正常に動作する

2. **API呼び出し確認**
   - [ ] Network タブでAPI呼び出しURL確認: `http://localhost:8000/api/auth/*`
   - [ ] レスポンスが正常に返される（成功またはエラー問わず）

#### 8.2 Observer機能テスト

1. **音声チャット画面確認**
   - [ ] 音声チャット画面にアクセスできる
   - [ ] UI要素が正常に表示される

2. **Observer API呼び出し確認**
   - [ ] Network タブでAPI呼び出しURL確認: `http://localhost:8000/api/observer/*`
   - [ ] 各種Observer機能のAPIが正しいエンドポイントを呼び出している

### 9. エラーハンドリング確認

#### 9.1 環境変数未設定時のテスト

1. **一時的に.env.localをリネーム**

   ```bash
   mv .env.local .env.local.backup
   ```

2. **デフォルト値確認**

   ```bash
   npm run dev
   ```

   - [ ] アプリケーションが起動する
   - [ ] デフォルト値（localhost:8000）が使用される

3. **ファイルを戻す**

   ```bash
   mv .env.local.backup .env.local
   ```

#### 9.2 バックエンド接続エラー時のテスト

1. **backendサーバーを停止**
2. **フロントエンドでAPI呼び出し操作を実行**
   - [ ] 適切なエラーハンドリングが動作する
   - [ ] アプリケーションがクラッシュしない
   - [ ] ユーザーに分かりやすいエラーメッセージが表示される

### 10. パフォーマンス確認

#### 10.1 起動時間確認

```bash
# 開発サーバーの起動時間を測定
time npm run dev
```

#### 10.2 ビルド時間確認

```bash
# ビルド時間を測定
time npm run build
```

#### 10.3 Chrome DevTools Performance確認

1. ブラウザでページを開く
2. 開発者ツール > Performance タブ
3. 録画を開始してページをリロード
4. パフォーマンスメトリクスを確認

### 11. コード品質確認

#### 11.1 TypeScript型安全性確認

```typescript
// 以下のコードをテスト用ファイルに記述して型チェック
import { environment } from '@/config/environment';

// ✅ これは動作する
const apiUrl = environment.apiBaseUrl;
const appName = environment.appName;

// ❌ これは型エラーになるべき
// const invalid = environment.nonExistentProperty;
```

#### 11.2 import文の一貫性確認

```bash
# すべてのファイルでimport文が統一されているか確認
grep -r "from '@/config/environment'" src/
```

## ローカル検証チェックリスト

### 環境確認

- [x] Node.js 18以上がインストール済み
- [x] npm/yarnがインストール済み
- [x] backendサーバーが利用可能

### ファイル確認

- [x] .env.localが作成されている
- [x] .env.exampleの内容が適切
- [x] src/config/environment.tsが作成されている
- [x] 5つのファイルでimport文が追加されている
- [x] process.env直接参照が削除されている

### ビルド確認

- [x] TypeScriptコンパイルが成功
- [x] ESLintチェックが成功
- [x] Next.jsビルドが成功
- [x] 開発サーバーが正常起動

### 機能確認

- [x] 環境変数が正しく読み込まれている
- [x] API呼び出しURLが localhost:8000 になっている
- [x] 認証機能が動作する
- [x] Observer機能が動作する
- [x] エラーハンドリングが適切

### 品質確認

- [x] TypeScript型安全性が確保されている
- [x] パフォーマンスに問題がない
- [x] コード品質が向上している

## 問題発生時の対応

### よくある問題と解決方法

1. **TypeScriptコンパイルエラー**

   ```bash
   # パスエイリアスの問題の場合
   npm run dev -- --turbo=false
   ```

2. **import文でエラーが出る**

   ```bash
   # tsconfig.jsonのpathsが正しいか確認
   cat tsconfig.json | grep -A5 "paths"
   ```

3. **環境変数が読み込まれない**

   ```bash
   # .env.localファイルの文法確認
   cat -A .env.local  # 隠れ文字確認
   ```

4. **開発サーバーが起動しない**

   ```bash
   # node_modules再インストール
   rm -rf node_modules package-lock.json
   npm install
   ```

### ロールバック手順

1. **コード変更の巻き戻し**

   ```bash
   git stash  # 現在の変更を一時保存
   git checkout HEAD~1  # 前のコミットに戻る
   ```

2. **部分的なロールバック**

   ```bash
   # 特定ファイルのみ戻す
   git checkout HEAD~1 -- src/config/environment.ts
   git checkout HEAD~1 -- src/utils/auth/apiClient.ts
   ```

## 検証完了基準

すべてのチェックリスト項目が ✅ になり、以下の条件を満たしていること:

1. **機能的要件**
   - アプリケーションが正常に起動する
   - すべてのAPI呼び出しが正しいエンドポイント（localhost:8000）に向かう
   - 既存機能にデグレードが発生していない

2. **非機能的要件**
   - TypeScriptコンパイルエラーがない
   - ESLintエラーがない（新規エラーなし）
   - パフォーマンスに問題がない

3. **品質要件**
   - 型安全性が確保されている
   - コードの可読性・保守性が向上している
   - セキュリティに問題がない

## 次のステップ

ローカル検証が完了し、すべてのチェック項目が ✅ になったら、`aws_test.md` に進んでAWS環境での検証を実施する。
