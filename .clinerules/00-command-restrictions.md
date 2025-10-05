# コマンド実行制限

## 禁止コマンド

### システム関連

- `sudo`
- gitで未追跡の`rm`
- `chmod 777`

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
