# コマンド実行制限

## 禁止コマンド

### システム関連

- `sudo`
- `rm -rf`
- gitで未追跡の`rm`
- `chmod 777`
- `dd`

### Git関連

- `git add`
- `git commit`
- `git push --force`
- `git reset --hard`
- `git rebase -i`
- `git branch -D`
- `git tag -d`

## 制限理由

データ損失・セキュリティ・本番環境・協業への影響防止

## 代替案

- `rm -rf` → `rm -r`または個別削除
- `sudo` → ユーザーが手動実行
- `git push --force` → `git push --force-with-lease`
- `git reset --hard` → `git reset --soft`または`git checkout`
- `git branch -D` → `git branch -d`（マージ済み確認後）

緊急時はユーザーが直接実行すること。
