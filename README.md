# ![logo](assets/logo.png)

**Lecturia** は、LLM（大規模言語モデル）を活用してトピックからインタラクティブな講義を自動生成・再生するシステムです。

## 🎯 特徴

- **自動講義生成**: トピックを入力するだけで、構造化されたスライドと音声付き講義を自動生成
- **キャラクター演出**: 複数のキャラクターによる対話形式の講義をサポート
- **リアルタイム再生**: スライドとタイムライン制御された音声・アニメーションの同期再生
- **多様な音声**: 複数の音声タイプ（TTS）に対応
- **クラウド統合**: Google Cloud Storage を活用したスケーラブルなアセット管理

## 🏗️ アーキテクチャ

Lecturia は以下の2つの主要コンポーネントで構成されています：

### API（Python/FastAPI）
LLM チェーンを用いてトピックからインタラクティブな講義を生成するバックエンドサービス

### Web（Next.js/React）
生成された講義を表示・再生するフロントエンド

## 🔄 コアワークフロー

1. **スライド生成**: LangChain を用いてトピックから HTML スライドを生成
2. **スクリプト作成**: スライドをキャラクター割り当て付きの話者スクリプトに変換
3. **音声生成**: 各スライドに対して TTS 音声を生成
4. **イベント抽出**: 音声とスライドからキャラクターアニメーションや遷移のタイムラインイベントを生成
5. **講義の組み立て**: すべての要素を統合して再生可能な講義データを作成

## 🚀 セットアップ

### API（バックエンド）
バックエンドのセットアップについては、[api/README.md](api/README.md) を参照してください。

### Web（フロントエンド）
フロントエンドのセットアップについては、[web/README.md](web/README.md) を参照してください。

## 📋 主要コンポーネント

### API コア
- `models.py`: データモデル定義（MovieConfig, Event, Character, Manifest）
- `router.py`: 講義管理用 REST API エンドポイント
- `server.py`: FastAPI アプリケーションと CORS 設定
- `chains/`: コンテンツ生成用の LangChain コンポーネント
- `cloud_pipeline/workflow.py`: 講義生成のメインワークフロー
- `storage.py`: Google Cloud Storage との統合

### チェーンモジュール
- `slide_maker.py`: トピックから HTML スライドを生成
- `slide_to_script.py`: スライドを話者スクリプトに変換
- `tts.py`: 複数の音声タイプによるテキスト読み上げ音声生成
- `event_extractor.py`: 音声とスライドからタイムラインイベントを抽出
- `sprite_generator.py`: キャラクタースプライトの管理

### Web コンポーネント
- `app/lectures/[id]/page.tsx`: 講義再生ページ
- `components/Player.tsx`: 講義の再生コンポーネント
- `hooks/useTimeline.ts`: タイムライン状態管理用フック

## 📊 データフロー

1. ユーザーが `MovieConfig`（トピックやキャラクター設定）を送信
2. システムが スライド → スクリプト → 音声 → イベント → 最終マニフェストを生成
3. 全てのアセットは Google Cloud Storage に保存
4. Web クライアントがマニフェストを取得し、同期再生を実行

## 🔧 技術スタック

- **Backend**: Python, FastAPI, LangChain, Google Cloud Tasks
- **Frontend**: Next.js, React, TypeScript
- **Storage**: Google Cloud Storage
- **Audio**: TTS (Text-to-Speech) 音声生成
