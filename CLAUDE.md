# CLAUDE.md

このファイルは、Claude Code（claude.ai/code）がこのリポジトリのコードを扱う際のガイドラインを提供します。

## プロジェクト構成

Lecturia は、講義の生成と再生を行うシステムで、以下の 2 つの主要なコンポーネントがあります：

* **API（Python/FastAPI）**: LLM チェーンを用いてトピックからインタラクティブな講義を生成するバックエンドサービス
* **Web（Next.js/React）**: 生成された講義を表示・再生するフロントエンド

## よく使うコマンド

### API 開発

```bash
cd api
docker compose up -d
```

### Web 開発

```bash
cd web
pnpm dev                   # 開発サーバーを localhost:3000 で起動
pnpm build                # 本番用にビルド
pnpm lint                 # Lint チェックを実行
```

## アーキテクチャ概要

### コアワークフロー

1. **スライド生成**: LangChain を用いてトピックから HTML スライドを生成
2. **スクリプト作成**: スライドをキャラクター割り当て付きの話者スクリプトに変換
3. **音声生成**: 各スライドに対して TTS 音声を生成
4. **イベント抽出**: 音声とスライドからキャラクターアニメーションや遷移のタイムラインイベントを生成
5. **講義の組み立て**: すべての要素を統合して再生可能な講義データを作成

### 主要コンポーネント

**API コア (`api/src/lecturia/`)**:

* `models.py`: データモデル定義（MovieConfig, Event, Character, Manifest）
* `router.py`: 講義管理用 REST API エンドポイント
* `server.py`: FastAPI アプリケーションと CORS 設定
* `chains/`: コンテンツ生成用の LangChain コンポーネント
* `cloud_pipeline/workflow.py`: 講義生成のメインワークフロー
* `storage.py`: Google Cloud Storage との統合

**チェーンモジュール (`api/src/lecturia/chains/`)**:

* `slide_maker.py`: トピックから HTML スライドを生成
* `slide_to_script.py`: スライドを話者スクリプトに変換
* `tts.py`: 複数の音声タイプによるテキスト読み上げ音声生成
* `event_extractor.py`: 音声とスライドからタイムラインイベントを抽出
* `sprite_generator.py`: キャラクタースプライトの管理

**Web コンポーネント (`web/`)**:

* `app/lectures/[id]/page.tsx`: 講義再生ページ
* `components/Player.tsx`: 講義の再生コンポーネント
* `hooks/useTimeline.ts`: タイムライン状態管理用フック

### データフロー

1. ユーザーが `MovieConfig`（トピックやキャラクター設定）を送信
2. システムが スライド → スクリプト → 音声 → イベント → 最終マニフェストを生成
3. 全てのアセットは Google Cloud Storage に保存
4. Web クライアントがマニフェストを取得し、同期再生を実行

### 主なモデル

* `MovieConfig`: トピックやキャラクター設定などの入力情報
* `Event`: アニメーションや遷移用のタイムラインイベント
* `Character`: 音声やスプライト情報を含む話者定義
* `Manifest`: 講義の再生用メタデータ

## 開発メモ

* 非同期の講義生成には Google Cloud Tasks を使用
* 音声処理には無音部分の除去とセグメントタイミングの調整を含む
* キャラクタースプライトはマニフェスト内に base64 で埋め込み
* スライド遷移は音声の長さ + 遅延設定によりタイミング制御される

