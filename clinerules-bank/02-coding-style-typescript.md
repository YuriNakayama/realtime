# コーディングガイドライン

## 一般原則

- DRY (Don't Repeat Yourself) 原則を守る
- SOLID原則に従う
- 単一責任の原則を遵守する
- 複雑な条件よりも早期リターンを優先する
- 副作用を最小限に抑え、純粋関数を優先する
- クラスよりも関数とComposition APIを優先する

## TypeScript規約

- すべての関数、変数に明示的な型定義を使用する
- any型の使用は避ける、必要な場合はunknownを使用する
- インターフェースよりも型エイリアス (type) を優先する
- Zodによる実行時の型検証を使用する
- 複雑な型にはコメントで説明を追加する
- インデックスシグネチャの使用は避ける

### 良い例

```typescript
type UserId = string;
type UserData = {
  id: UserId;
  name: string;
  email: string;
  createdAt: Date;
  settings: UserSettings;
};
```

### 避けるべき例

```typescript
type Data = any;
```

## Reactコンポーネント規約

- コンポーネントはアトミックデザイン原則に従う
- React.FCの使用は避ける（TypeScriptの型推論を活用）
- Props型は各コンポーネントの直前に定義する
- デフォルトProps値はES6のデフォルトパラメータを使用する
- コンポーネントファイル名はPascalCaseを使用する
- ロジックとUIを分離し、カスタムフックに抽出する

### 良い例

```typescript
type ButtonProps = {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  children: React.ReactNode;
};

function Button({
  variant = 'primary',
  size = 'md',
  onClick,
  children
}: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

## 状態管理

- ローカルな状態には `useState` を使用する
- 複雑な状態には `useReducer` を使用する
- グローバル状態には Context API を使用する
- サーバー状態には Tanstack Query または SWR を使用する
- 状態の更新は不変性を保つ
- ステート管理の最適化のためメモ化を適切に使用する

## API通信

- API関数は `/lib/api` に集約する
- エラーハンドリングは一貫したパターンで行う
- データフェッチには SWR または React Query を使用する
- アクセストークンの扱いには注意する
- API呼び出しは型安全にする
- レスポンスは必ず型検証を行う

### 良い例

```typescript
async function fetchUser(id: string): Promise<UserData> {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      throw new ApiError(`Failed to fetch user: ${response.statusText}`, response.status);
    }
    const data = await response.json();
    // Zodで型検証
    return userSchema.parse(data);
  } catch (error) {
    handleApiError(error);
    throw error;
  }
}
```
