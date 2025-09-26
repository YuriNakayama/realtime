# Frontend環境変数管理変更 - AWS環境検証

## 検証の目的

ローカルホストでの動作確認は行わない

## AWS環境での検証手順

### 1. デプロイ前準備

#### 1.3 現在のブランチ確認

```bash
# 現在のブランチとコミット状況を確認
git status
git log --oneline -5
```

### 2. デプロイ実行

#### 2.1 コミットとプッシュ

```bash
# 変更をコミット（未コミットの場合）
git add .
git commit -m "feat: 環境変数管理を集約化（environment.ts導入）

- src/config/environment.tsを作成し、型安全な環境変数アクセスを実装
- 5つのファイルでprocess.env直接参照をenvironment.ts経由に変更
- .env.localファイルをローカル開発用として作成
- 環境変数の一元管理によりコード保守性を向上"

# リモートリポジトリにプッシュ
git push origin hotfix/env_parameter
```

#### 2.2 自動デプロイ監視

1. **AWS Amplifyコンソールでデプロイ監視**
   - プッシュ後、自動的にビルドが開始されることを確認
   - ビルドステータスを監視：
     - Provision: ✅
     - Build: ✅  
     - Deploy: ✅
     - Verify: ✅

2. **ビルドログ確認**
   - 各ステップのログを確認
   - 特に「Build」ステップで以下を確認：
     - TypeScriptコンパイルエラーがない
     - 環境変数が正しく読み込まれている
     - Next.jsビルドが成功している

#### 2.3 デプロイ完了確認

```bash
# デプロイ完了後のドメインを確認
echo "デプロイされたURL: https://hotfix-fix-connection-error.dctmsy7y5wlxk.amplifyapp.com"
```

### 3. AWS環境での動作確認

#### 3.1 アプリケーション起動確認

1. **本番URLにアクセス**
   - ブラウザで本番URLを開く
   - ページが正常に読み込まれることを確認
   - ローディング時間が許容範囲内であることを確認

2. **基本UI確認**
   - [ ] メインページが表示される
   - [ ] ナビゲーションメニューが正常に動作する
   - [ ] レスポンシブデザインが正常に動作する

#### 3.2 環境変数動作確認

1. **ブラウザ開発者ツールでの確認**
   - F12で開発者ツールを開く
   - Networkタブを選択
   - ページをリロードまたはAPI操作を実行

2. **API呼び出しURL確認**
   - Network タブでAPI呼び出しを確認
   - 全てのAPI呼び出しが本番エンドポイント（<https://api.dev.legal-ai-reception.click）に向かっていることを確認>
   - localhost:8000へのリクエストが存在しないことを確認

3. **環境変数値確認**
   - Consoleタブで以下を実行して間接的に確認：

   ```javascript
   // ページタイトルやUI要素から環境変数値を推測
   console.log('Page title:', document.title);
   console.log('Current domain:', window.location.hostname);
   ```

### 4. 機能動作確認

#### 4.1 認証機能テスト

1. **ユーザー登録テスト**
   - [ ] 新規ユーザー登録画面にアクセス
   - [ ] フォーム入力が正常に動作する
   - [ ] Network タブでAPI呼び出し確認: `https://api.dev.legal-ai-reception.click/api/auth/signup`
   - [ ] 適切なレスポンス（成功/エラー）を受信する

2. **ログインテスト**
   - [ ] ログイン画面にアクセス
   - [ ] 既存ユーザーでログイン試行
   - [ ] Network タブでAPI呼び出し確認: `https://api.dev.legal-ai-reception.click/api/auth/login`
   - [ ] セッション管理が正常に動作する

3. **ログアウトテスト**
   - [ ] ログアウト機能を実行
   - [ ] Network タブでAPI呼び出し確認: `https://api.dev.legal-ai-reception.click/api/auth/logout`
   - [ ] セッション情報が適切にクリアされる

#### 4.2 音声チャット機能テスト

1. **音声チャット画面確認**
   - [ ] 音声チャット画面にアクセス
   - [ ] WebSocket接続が正常に確立される
   - [ ] マイク・スピーカーのアクセス許可が正常に動作する

2. **Realtime API接続確認**
   - [ ] OpenAI Realtime APIへの接続が成功する
   - [ ] 音声入力・出力が正常に動作する
   - [ ] Network タブでWebSocket通信を確認

#### 4.3 Observer機能テスト

1. **Observer API呼び出し確認**
   - [ ] Network タブでObserver関連API確認:
     - `https://api.dev.legal-ai-reception.click/api/observer/insights`
     - `https://api.dev.legal-ai-reception.click/api/observer/observe`
     - `https://api.dev.legal-ai-reception.click/api/observer/hearing`

2. **機能動作確認**
   - [ ] インサイト生成が正常に動作する
   - [ ] ヒアリング項目管理が正常に動作する
   - [ ] Observer AIの各種分析機能が動作する

### 5. パフォーマンス確認

#### 5.1 Chrome DevTools Performance測定

1. **Lighthouse監査**
   - 開発者ツール > Lighthouse タブ
   - 「Generate report」を実行
   - スコア確認：
     - [ ] Performance: 80以上
     - [ ] Accessibility: 90以上  
     - [ ] Best Practices: 90以上
     - [ ] SEO: 90以上

2. **Core Web Vitals確認**
   - [ ] LCP (Largest Contentful Paint): 2.5秒以下
   - [ ] FID (First Input Delay): 100ms以下
   - [ ] CLS (Cumulative Layout Shift): 0.1以下

#### 5.2 ページロード時間測定

```javascript
// ブラウザConsoleで実行
console.log('Page load time:', performance.timing.loadEventEnd - performance.timing.navigationStart, 'ms');
```

#### 5.3 API レスポンス時間確認

- Network タブで各API呼び出しの応答時間を確認
- [ ] 認証API: 1秒以下
- [ ] Observer API: 3秒以下
- [ ] その他API: 2秒以下

### 6. セキュリティ確認

#### 6.1 環境変数漏洩チェック

1. **クライアントサイド確認**
   - ブラウザ開発者ツール > Sources タブ
   - ビルドされたJavaScriptファイルを検索
   - 機密情報（API キー等）が含まれていないことを確認

2. **Network リクエスト確認**
   - [ ] NEXT_PUBLIC_* 以外の環境変数がクライアントに送信されていない
   - [ ] API キーやシークレット情報がリクエストヘッダーやボディに含まれていない

#### 6.2 HTTPS接続確認

- [ ] すべての通信がHTTPS経由で行われている
- [ ] Mixed Content警告が発生していない
- [ ] SSL証明書が有効である

### 7. エラーハンドリング確認

#### 7.1 API エラー時の動作

1. **バックエンドAPI停止シミュレーション**
   - 開発者ツール > Network タブ
   - 「Offline」モードを有効にする
   - API を使用する操作を実行

2. **エラーハンドリング確認**
   - [ ] 適切なエラーメッセージが表示される
   - [ ] アプリケーションがクラッシュしない
   - [ ] ユーザーに復旧方法が提示される

#### 7.2 環境変数設定エラー時の動作

1. **環境変数不備シミュレーション**
   - AWS Amplifyで一時的に環境変数を削除または変更
   - 再デプロイを実行

2. **フォールバック動作確認**
   - [ ] デフォルト値が使用される
   - [ ] アプリケーションが正常に起動する
   - [ ] エラーログが適切に出力される

### 8. 回帰テスト

#### 8.1 既存機能確認

1. **認証フロー**
   - [ ] ユーザー登録 → ログイン → ダッシュボード遷移が正常
   - [ ] セッション管理が正常に動作
   - [ ] アクセス制御が適切に機能

2. **音声チャット機能**
   - [ ] リアルタイム音声対話の開始/停止
   - [ ] 音声認識・合成が正常に動作
   - [ ] WebSocket接続が安定

3. **Observer Agent機能**
   - [ ] 会話の観察とインサイト生成
   - [ ] ヒアリング項目の自動更新
   - [ ] 各種AI分析機能

4. **UI/UX機能**
   - [ ] レスポンシブデザイン
   - [ ] アニメーション・トランジション
   - [ ] フォーム入力・バリデーション

### 9. クロスブラウザ確認

#### 9.1 主要ブラウザでの動作確認

1. **Chrome（最新版）**
   - [ ] 基本機能が正常に動作
   - [ ] パフォーマンスが良好

2. **Firefox（最新版）**
   - [ ] 基本機能が正常に動作
   - [ ] CSS・JavaScript互換性

3. **Safari（最新版）**
   - [ ] 基本機能が正常に動作
   - [ ] WebKit特有の問題がない

4. **Edge（最新版）**
   - [ ] 基本機能が正常に動作
   - [ ] Chromium基盤での互換性

#### 9.2 モバイルブラウザ確認

1. **iOS Safari**
   - [ ] タッチ操作が正常
   - [ ] 音声機能がモバイルで動作

2. **Android Chrome**
   - [ ] タッチ操作が正常
   - [ ] 音声機能がモバイルで動作

## AWS環境検証チェックリスト

### デプロイ確認

- [ ] AWS Amplify環境変数が正しく設定されている
- [ ] 自動デプロイが成功している
- [ ] ビルドログにエラーがない
- [ ] 本番URLにアクセスできる

### 環境変数動作確認

- [x] 全APIリクエストが本番エンドポイントに向かう
- [x] localhost:8000への不適切なリクエストがない
- [x] environment.tsが正しく動作している

### 機能確認

- [ ] 認証機能が正常に動作する
- [ ] 音声チャット機能が正常に動作する
- [ ] Observer機能が正常に動作する
- [ ] 全UI/UX機能が正常に動作する

### パフォーマンス確認

- [ ] Lighthouseスコアが基準値以上
- [ ] Core Web Vitalsが良好
- [ ] API応答時間が許容範囲内
- [ ] ページロード時間が良好

### セキュリティ確認

- [ ] 機密情報の漏洩がない
- [ ] HTTPS通信が正常
- [ ] SSL証明書が有効
- [ ] セキュリティヘッダーが適切

### 互換性確認

- [ ] 主要ブラウザで正常動作
- [ ] モバイルブラウザで正常動作
- [ ] クロスプラットフォーム互換性

### 監視・運用確認

- [ ] CloudWatchログが正常
- [ ] エラー率が許容範囲内
- [ ] パフォーマンスメトリクスが良好
