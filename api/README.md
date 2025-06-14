# Lecturia API

Lecturia バックエンドは、Python/FastAPI を使用して構築された講義生成システムです。LangChain を活用してトピックからインタラクティブな講義を自動生成します。

## 🚀 クイックスタート

### Docker を使用した起動（推奨）

```bash
cd api
docker compose up -d
```

APIサーバーは `http://localhost:8000` で起動します。

### 手動セットアップ

1. **Python環境の準備**
   ```bash
   cd api
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   ```

3. **環境変数の設定**
   ```bash
   cp .env.example .env
   # .env ファイルを編集して必要な環境変数を設定
   ```

4. **サーバーの起動**
   ```bash
   uvicorn src.lecturia.server:app --reload --host 0.0.0.0 --port 8000
   ```

## 🔧 環境変数

以下の環境変数を `.env` ファイルに設定してください：

- `OPENAI_API_KEY`: OpenAI API キー（LLM チェーン用）
- `GOOGLE_CLOUD_PROJECT`: Google Cloud プロジェクト ID
- `GOOGLE_CLOUD_STORAGE_BUCKET`: Google Cloud Storage バケット名
- その他、必要に応じて追加の環境変数

## 📁 プロジェクト構造

```
api/
├── src/lecturia/
│   ├── models.py              # データモデル定義
│   ├── router.py              # REST API エンドポイント
│   ├── server.py              # FastAPI アプリケーション
│   ├── storage.py             # Google Cloud Storage 統合
│   ├── chains/                # LangChain コンポーネント
│   │   ├── slide_maker.py     # スライド生成
│   │   ├── slide_to_script.py # スクリプト変換
│   │   ├── tts.py             # 音声生成
│   │   ├── event_extractor.py # イベント抽出
│   │   └── sprite_generator.py # スプライト管理
│   └── cloud_pipeline/
│       └── workflow.py        # メインワークフロー
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 🔄 講義生成ワークフロー

1. **MovieConfig** を受信（トピック、キャラクター設定など）
2. **スライド生成**: LangChain でトピックから HTML スライドを作成
3. **スクリプト変換**: スライドをキャラクター付き話者スクリプトに変換
4. **音声生成**: TTS を使用して各スライドの音声を生成
5. **イベント抽出**: 音声とスライドからタイムラインイベントを抽出
6. **マニフェスト作成**: すべての要素を統合した再生用データを作成

## 🛠️ 開発

### API ドキュメント

サーバー起動後、以下の URL で API ドキュメントを確認できます：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### テスト実行

```bash
pytest
```

### コードフォーマット

```bash
black src/
isort src/
```

## 🏗️ デプロイ

### Google Cloud Run への デプロイ

```bash
# Docker イメージをビルド
docker build -t lecturia-api .

# Google Cloud Registry にプッシュ
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/lecturia-api

# Cloud Run にデプロイ
gcloud run deploy lecturia-api \
    --image gcr.io/YOUR_PROJECT_ID/lecturia-api \
    --platform managed \
    --region asia-northeast1 \
    --allow-unauthenticated
```

## 📝 補足

- 非同期の講義生成には Google Cloud Tasks を使用
- 音声処理には無音部分の除去とセグメントタイミングの調整を含む
- キャラクタースプライトはマニフェスト内に base64 で埋め込み
- スライド遷移は音声の長さ + 遅延設定によりタイミング制御される
