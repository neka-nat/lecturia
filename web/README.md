# lecturia web

## Getting Started

```bash
cp .env.example .env
# edit .env
```

Install dependencies:

```bash
pnpm install
```

First, run the development server:

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.


## Deploy

```bash
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_API_ORIGIN=<API_URL>

gcloud run deploy lecturia-frontend \
  --image asia-northeast1-docker.pkg.dev/$PROJECT_ID/lecturia-frontend/lecturia-frontend:latest \
  --region asia-northeast1
```
