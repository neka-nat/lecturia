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
gcloud run deploy --update-env-vars NEXT_PUBLIC_LECTURIA_API_ORIGIN=<API_URL>
```
