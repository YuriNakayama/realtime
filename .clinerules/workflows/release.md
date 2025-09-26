# Release 作成指示（Cline用）

リリースの準備が完了し、`main`ブランチが最新の状態であることを前提として、以下の指示に従ってreleaseを作成してください。

## Clineへの指示

### 前提条件

- `main`ブランチに最新の変更がマージされていること
- すべてのテストが通過していること
- デプロイメントが正常に完了していること
- リリースノートの準備ができていること

### 実行手順

1. **リリース準備の確認**

   ```bash
   # 最新のmainブランチに切り替え
   git checkout main
   git pull origin main
   
   # 現在の状況確認
   git status
   git log --oneline -5
   ```

2. **タグ作成前の確認**

   ```bash
   # 既存のタグ確認
   git tag --sort=-version:refname | head -10
   
   # 現在のブランチ確認
   git branch --show-current
   ```

3. **リリースバージョンの確認**

   **ユーザーに確認する項目：**
   - 新しいリリースバージョン（例：v1.2.3）
   - プレリリースか通常リリースか

   **リリースタイトルは自動生成：** バージョンのみ（例：v1.2.3）

4. **セマンティックバージョニングに基づくタグ作成**

   ```bash
   # 新しいバージョンタグ作成（ユーザー確認済みバージョン）
   git tag -a v<USER_CONFIRMED_VERSION> -m "Release v<USER_CONFIRMED_VERSION>"
   
   # タグをリモートにプッシュ
   git push origin v<USER_CONFIRMED_VERSION>
   ```

5. **GitHub CLI を使用してリリース作成**

   ```bash
   # GitHub Releaseの作成（タイトルはバージョンのみ）
   TODAY=$(date +%Y/%m/%d)
   
   # 一時的なリリースノートファイルを作成
   cat > temp_release_notes.md << EOF
   **リリース日時:** $TODAY
   
   ## 概要
   このリリースの主な変更点と改善
   
   ## 主な変更点
   - [手動で追加する主要な変更点]
   
   EOF
   
   # 自動生成されたWhat's Changedを追加
   echo "## What's Changed" >> temp_release_notes.md
   gh api repos/:owner/:repo/releases/generate-notes \
     -f tag_name="v<USER_CONFIRMED_VERSION>" \
     --jq '.body' >> temp_release_notes.md
   
   # リリース作成（通常リリースは--latest、プレリリースは--prereleaseを使用）
   gh release create v<USER_CONFIRMED_VERSION> \
     --title "v<USER_CONFIRMED_VERSION>" \
     --notes-file temp_release_notes.md \
     --latest
   
   # 一時ファイル削除
   rm temp_release_notes.md
   ```

6. **リリース後の確認**

   ```bash
   # リリース確認
   gh release view v<USER_CONFIRMED_VERSION>
   
   # デプロイメント状況確認
   gh run list --workflow="CD Backend" --limit=5
   ```

### バージョニング規則

**セマンティックバージョニング（SemVer）**に従う：

- **MAJOR**: 破壊的変更がある場合
- **MINOR**: 後方互換性を保った機能追加
- **PATCH**: 後方互換性を保ったバグ修正

### 自動デプロイメント

タグプッシュ後、以下が自動実行される：

1. **CI/CDパイプライン**: GitHub Actions によるビルド・テスト
2. **デプロイメント**: `main` ブランチのAWS本番環境への自動デプロイ
3. **通知**: デプロイメント結果の通知

### 注意事項

- **mainブランチからのみ**リリースを作成すること
- リリース前に**本番環境での動作確認**を完了すること
- **リリースノートは必須**で、変更内容を明確に記載すること
- **セマンティックバージョニング**を厳密に守ること
- **リリースタイトルは自動生成**され、バージョンのみの形式とする
- **タイトルのユーザー確認は不要**
- **リリース日時は本文に記載**する
- **通常リリースは`--latest`、プレリリースは`--prerelease`オプションを使用**すること
