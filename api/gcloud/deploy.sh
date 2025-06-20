#!/usr/bin/env bash
set -e

# Dockerイメージのビルドとプッシュ
gcloud builds submit --tag $REPOSITORY_URL --project $GOOGLE_CLOUD_PROJECT

# apiのデプロイ
gcloud run deploy $CLOUD_RUN_API_SERVICE_NAME --image $REPOSITORY_URL \
    --region $GOOGLE_CLOUD_LOCATION --project $GOOGLE_CLOUD_PROJECT --timeout=60m \
    --command "fastapi" \
    --args "run,src/lecturia/server.py,--port,8080" \
    --service-account $CLOUD_RUN_API_SERVICE_ACCOUNT --memory=2Gi \
    --update-env-vars LECTURIA_WORKER_URL=$LECTURIA_WORKER_URL \
    --update-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
    --update-env-vars GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION \
    --update-env-vars GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME=$GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME \
    --update-env-vars CORS_ALLOWED_ORIGINS=$CORS_ALLOWED_ORIGINS \
    --allow-unauthenticated

# Workerのデプロイ
gcloud run deploy $CLOUD_RUN_WORKER_SERVICE_NAME --image $REPOSITORY_URL \
    --region $GOOGLE_CLOUD_LOCATION --project $GOOGLE_CLOUD_PROJECT --timeout=60m \
    --command "fastapi" \
    --args "run,src/lecturia/cloud_pipeline/workflow.py,--port,8080" \
    --service-account $CLOUD_RUN_WORKER_SERVICE_ACCOUNT --memory=2Gi \
    --update-env-vars PROJECT_ID=$GOOGLE_CLOUD_PROJECT \
    --update-env-vars SUBSCRIPTION_ID=$CLOUD_RUN_SUBSCRIPTION_ID \
    --update-env-vars GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME=$GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME \
    --set-secrets=ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,GOOGLE_API_KEY=GOOGLE_API_KEY:latest,BRAVE_API_KEY=BRAVE_API_KEY:latest \
    --allow-unauthenticated
