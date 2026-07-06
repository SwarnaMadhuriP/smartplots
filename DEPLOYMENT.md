# SmartPlots Deployment Guide

This guide prepares SmartPlots for a production-style deployment on Google Cloud
Platform while preserving the existing local Docker PostgreSQL workflow.

## Architecture

```text
Vercel Next.js frontend
        |
        v
Google Cloud Run FastAPI backend
        |
        v
PostgreSQL + pgvector
        |
        v
Gemini 2.5 Flash + Google ADK agents + gemini-embedding-2
```

## Local Development

Local development keeps PostgreSQL in Docker.

1. Start PostgreSQL with pgvector from the repo root:

```bash
docker compose up -d
```

2. Configure the backend:

```bash
cp backend/.env.example backend/.env
```

Set:

```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/smartplots
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_GENAI_USE_VERTEXAI=False
FRONTEND_URL=http://localhost:3000
```

3. Run the backend:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

4. Run the frontend:

```bash
cd frontend
npm install
NEXT_PUBLIC_BACKENDAPI_BASE_URL=http://localhost:8000 npm run dev
```

5. Check backend health:

```bash
curl http://localhost:8000/health
```

## Backend Container

The backend Cloud Run image is built from `backend/Dockerfile`.

The container:

- Runs `app.main:app`, preserving existing API endpoints.
- Listens on the `PORT` environment variable, defaulting to `8080`.
- Reads `DATABASE_URL`, `GEMINI_API_KEY` or `GOOGLE_API_KEY`, and `FRONTEND_URL`
  from environment variables.
- Includes `backend/uploads` so demo document/RAG assets remain available.

Build locally:

```bash
docker build -t smartplots-backend ./backend
docker run --env-file backend/.env.local.example -p 8080:8080 smartplots-backend
```

## Required GCP APIs

Enable these APIs:

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com
```

`sqladmin.googleapis.com` is needed later if you attach Cloud SQL.

## Artifact Registry

Create a Docker repository:

```bash
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1
export REPOSITORY=smartplots

gcloud artifacts repositories create "$REPOSITORY" \
  --repository-format=docker \
  --location="$REGION" \
  --description="SmartPlots backend images" \
  --project="$PROJECT_ID"
```

Build and push with Cloud Build:

```bash
export IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/smartplots-backend:latest"

gcloud builds submit backend \
  --tag "$IMAGE_URI" \
  --project "$PROJECT_ID"
```

## Cloud Run Deployment

Use Cloud Run for the FastAPI backend.

Minimum environment variables:

```bash
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
FRONTEND_URL=https://your-smartplots-frontend.vercel.app
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_GENAI_USE_VERTEXAI=False
```

Deploy manually:

```bash
gcloud run deploy smartplots-backend \
  --image "$IMAGE_URI" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=$DATABASE_URL,FRONTEND_URL=$FRONTEND_URL,GOOGLE_GENAI_USE_VERTEXAI=False" \
  --set-secrets "GEMINI_API_KEY=smartplots-gemini-api-key:latest" \
  --project "$PROJECT_ID"
```

Or use the deploy script:

```bash
cd backend
PROJECT_ID=your-gcp-project-id \
REGION=us-central1 \
REPOSITORY=smartplots \
DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE" \
FRONTEND_URL="https://your-smartplots-frontend.vercel.app" \
GEMINI_API_KEY_SECRET=smartplots-gemini-api-key \
./deploy.sh
```

If you do not use Secret Manager yet, you can pass `GEMINI_API_KEY`, but Secret
Manager is safer for production.

## Gemini And ADK Configuration

SmartPlots uses:

- `gemini-2.5-flash` for AI Advisor reasoning and AI Search explanation.
- `gemini-embedding-2` for RAG/document embeddings.
- Google ADK for the AI Search agent workflow.

Supported auth modes:

- `GEMINI_API_KEY` or `GOOGLE_API_KEY` with `GOOGLE_GENAI_USE_VERTEXAI=False`.
- Vertex AI auth with Cloud Run service account credentials and
  `GOOGLE_GENAI_USE_VERTEXAI=True`.

For the current deployment, use:

```bash
GEMINI_API_KEY=...
GOOGLE_GENAI_USE_VERTEXAI=False
```

## Cloud SQL Migration Later

Local development can continue using Docker PostgreSQL. When ready for Cloud SQL:

1. Create a PostgreSQL Cloud SQL instance.
2. Enable the `vector` extension in the production database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Attach Cloud SQL to Cloud Run:

```bash
export CLOUD_SQL_INSTANCE="PROJECT_ID:REGION:INSTANCE_NAME"
```

4. Use a Unix socket `DATABASE_URL`. The `host` value must be the Cloud SQL
   socket directory only; do not append `/.s.PGSQL.5432`.

```bash
DATABASE_URL="postgresql+psycopg://USER:PASSWORD@/DATABASE?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME"
```

5. Deploy with:

```bash
gcloud run deploy smartplots-backend \
  --image "$IMAGE_URI" \
  --region "$REGION" \
  --add-cloudsql-instances "$CLOUD_SQL_INSTANCE" \
  --set-env-vars "DATABASE_URL=$DATABASE_URL,FRONTEND_URL=$FRONTEND_URL,GOOGLE_GENAI_USE_VERTEXAI=False" \
  --set-secrets "GEMINI_API_KEY=smartplots-gemini-api-key:latest"
```

For the project/instance shown in the current demo, the database URL shape is:

```bash
DATABASE_URL='postgresql+psycopg://postgres:YOUR_URL_ENCODED_PASSWORD@/smartplots?host=/cloudsql/project-83505dd5-2674-4ab6-b02:us-central1:smartplots-postgres'
```

6. Seed or migrate production data separately. Do not point production Cloud Run
   at the local Docker database.

## Vercel Frontend

Deploy the `frontend/` directory to Vercel.

Set this Vercel environment variable:

```bash
NEXT_PUBLIC_BACKENDAPI_BASE_URL=https://your-cloud-run-service-url
```

Then set the matching backend CORS variable in Cloud Run:

```bash
FRONTEND_URL=https://your-smartplots-frontend.vercel.app
```

For Vercel preview deployments, add preview URLs to `ALLOW_ORIGINS` as a
comma-separated list.

## Production Checklist

- `docker compose up -d` still works for local PostgreSQL.
- `backend/Dockerfile` builds the FastAPI API service.
- `/health` returns `{"status":"ok"}`.
- `DATABASE_URL` is set in Cloud Run.
- `GEMINI_API_KEY` or `GOOGLE_API_KEY` is set securely.
- `FRONTEND_URL` matches the deployed Vercel URL.
- Vercel has `NEXT_PUBLIC_BACKENDAPI_BASE_URL` pointing to Cloud Run.
