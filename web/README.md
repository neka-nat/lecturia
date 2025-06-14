# Lecturia Web

Lecturia フロントエンドは、Next.js/React を使用して構築された講義再生システムです。生成された講義をインタラクティブに表示・再生します。

## 🚀 クイックスタート

### 前提条件

- Node.js 18.x 以降
- pnpm（推奨）または npm

### セットアップ

1. **依存関係のインストール**
   ```bash
   cd web
   pnpm install
   ```

2. **環境変数の設定**
   ```bash
   cp .env.example .env.local
   # .env.local ファイルを編集して必要な環境変数を設定
   ```

3. **開発サーバーの起動**
   ```bash
   pnpm dev
   ```

   サーバーは `http://localhost:3000` で起動します。

## 🔧 環境変数

以下の環境変数を `.env.local` ファイルに設定してください：

- `NEXT_PUBLIC_API_URL`: Lecturia API のベース URL（例：`http://localhost:8000`）
- その他、必要に応じて追加の環境変数

## 📁 プロジェクト構造

```
web/
├── app/
│   ├── lectures/
│   │   └── [id]/
│   │       └── page.tsx       # 講義再生ページ
│   ├── layout.tsx             # ルートレイアウト
│   └── page.tsx               # ホームページ
├── components/
│   ├── Player.tsx             # 講義再生コンポーネント
│   └── ...                    # その他のコンポーネント
├── hooks/
│   ├── useTimeline.ts         # タイムライン状態管理
│   └── ...                    # その他のカスタムフック
├── lib/
│   └── ...                    # ユーティリティ関数
├── public/
│   └── ...                    # 静的ファイル
├── styles/
│   └── ...                    # スタイルファイル
├── package.json
├── next.config.js
└── tailwind.config.js
```

## 🎬 主要機能

### 講義再生システム

- **同期再生**: スライドと音声のタイムライン制御による同期再生
- **キャラクターアニメーション**: 複数キャラクターによる対話演出
- **インタラクティブ操作**: 再生/停止、シーク、速度調整
- **レスポンシブデザイン**: デスクトップ・モバイル対応

### コアコンポーネント

- **Player.tsx**: 講義の再生を制御するメインコンポーネント
- **useTimeline.ts**: 音声とスライドの同期を管理するカスタムフック
- **lectures/[id]/page.tsx**: 講義IDに基づく動的な講義再生ページ

## 🛠️ 開発コマンド

### 開発サーバー
```bash
pnpm dev
```

### 本番ビルド
```bash
pnpm build
```

### 本番サーバー起動
```bash
pnpm start
```

### Lint チェック
```bash
pnpm lint
```

### 型チェック
```bash
pnpm type-check
```

## 🧪 テスト

### 単体テスト
```bash
pnpm test
```

### E2E テスト
```bash
pnpm test:e2e
```

## 🏗️ ビルド & デプロイ

### Vercel へのデプロイ（推奨）

1. Vercel アカウントに GitHub リポジトリを接続
2. 環境変数を Vercel ダッシュボードで設定
3. 自動デプロイが実行されます

### 手動デプロイ

```bash
# 本番ビルド
pnpm build

# 静的ファイルとして出力（必要に応じて）
pnpm export
```

## 🎨 カスタマイズ

### スタイリング

プロジェクトは Tailwind CSS を使用しています：

- `tailwind.config.js`: Tailwind の設定
- `app/globals.css`: グローバルスタイル

### コンポーネント

再利用可能なコンポーネントは `components/` ディレクトリに配置されています。

## 📱 対応ブラウザ

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🔧 トラブルシューティング

### よくある問題

1. **音声が再生されない**
   - ブラウザのオートプレイポリシーを確認
   - HTTPS 環境での実行を推奨

2. **API 接続エラー**
   - `NEXT_PUBLIC_API_URL` の設定を確認
   - CORS 設定を確認

3. **パフォーマンス問題**
   - 開発者ツールでネットワークタブを確認
   - 大きなアセットファイルの最適化を検討
