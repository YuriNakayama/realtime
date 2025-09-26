# Pull Request 作成指示

すべての変更がリモートリポジトリにpushされていることを前提として、以下の指示に従ってpull requestを作成してください。

## Clineへの指示

### 前提条件

- すべての変更がリモートブランチにpushされていること
- 現在のブランチが作業ブランチならば`develop`ブランチへ、現在のブランチが`develop`ブランチならば`main`ブランチへPRを作成すること

### 実行手順

1. **コミット履歴の確認**

   ```bash
   git log --oneline -10
   git log --graph --oneline --all -10
   ```

2. **現在のブランチ状況確認**

   ```bash
   git branch -a
   git status
   ```

3. **PRのテンプレートをコピー**

   ```bash
   cp .github/PULL_REQUEST_TEMPLATE.md tmp-pull-request-template.tmp
   ```

4. **PRの内容を確認・編集**

   - `tmp-pull-request-template.tmp` ファイルを開き、項目を適切に埋めてください

5. **タグの決定**

   ```bash
   # リストの中から適切なラベルを選択
   gh label list
   ```

6. **GitHub CLI を使用してPR作成**

   ```bash
   # PRを作成
   gh pr create \
     --base developもしくはmain \
     --head $(git branch --show-current) \
     --title "適切なタイトルを設定" \
     --body-file tmp-pull-request-template.tmp \
     --assignee @me \
     --label <name>
   
   # 一時ファイルを削除
   rm tmp-pull-request-template.tmp
   ```

### 設定項目

- **Base branch**: `develop` もしくは `main`（必須）
- **Head branch**: 現在の作業ブランチ
- **Assignee**: PR作成者（`@me`）
- **Template**: `.github/PULL_REQUEST_TEMPLATE.md`を使用
- **Labels**: 適切なラベルを追加（例: `bug`, `feature`, `documentation`など）

### 注意事項

- 作業ブランチから`main`ブランチへのPRの作成は禁止
- 変更内容を確認しタイトルはできるだけ具体的に書くこと
- Pull Requestテンプレートを必ず使用すること
- 常に適切なラベルを追加すること
