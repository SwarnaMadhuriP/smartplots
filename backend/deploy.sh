#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

: "${PROJECT_ID:?Set PROJECT_ID to your Google Cloud project ID.}"
: "${DATABASE_URL:?Set DATABASE_URL or use DATABASE_URL_SECRET with a custom deploy command.}"
: "${FRONTEND_URL:?Set FRONTEND_URL to your deployed frontend URL.}"

REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-smartplots-backend}"
REPOSITORY="${REPOSITORY:-smartplots}"
IMAGE_NAME="${IMAGE_NAME:-smartplots-backend}"
TAG="${TAG:-latest}"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${TAG}"
ENV_VARS="DATABASE_URL=${DATABASE_URL},FRONTEND_URL=${FRONTEND_URL},GOOGLE_GENAI_USE_VERTEXAI=${GOOGLE_GENAI_USE_VERTEXAI:-False}"

if [[ -n "${ALLOW_ORIGINS:-}" ]]; then
  ENV_VARS="${ENV_VARS},ALLOW_ORIGINS=${ALLOW_ORIGINS}"
fi

echo "Building ${IMAGE_URI}"
gcloud builds submit "${SCRIPT_DIR}" --tag "${IMAGE_URI}" --project "${PROJECT_ID}"

DEPLOY_ARGS=(
  run deploy "${SERVICE_NAME}"
  --image "${IMAGE_URI}"
  --region "${REGION}"
  --platform managed
  --allow-unauthenticated
  --project "${PROJECT_ID}"
  --set-env-vars "${ENV_VARS}"
)

if [[ -n "${GEMINI_API_KEY_SECRET:-}" ]]; then
  DEPLOY_ARGS+=(--set-secrets "GEMINI_API_KEY=${GEMINI_API_KEY_SECRET}:latest")
elif [[ -n "${GEMINI_API_KEY:-}" ]]; then
  DEPLOY_ARGS+=(--update-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}")
else
  echo "Warning: GEMINI_API_KEY or GEMINI_API_KEY_SECRET is not set."
fi

if [[ -n "${CLOUD_SQL_INSTANCE:-}" ]]; then
  DEPLOY_ARGS+=(--add-cloudsql-instances "${CLOUD_SQL_INSTANCE}")
fi

echo "Deploying ${SERVICE_NAME} to Cloud Run"
gcloud "${DEPLOY_ARGS[@]}"
