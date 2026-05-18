# SmartPlots

### AI-Powered Real Estate Intelligence  
Find Your Plot, Smarter.

## Overview

SmartPlots is an AI-powered real estate platform that helps users discover, analyze, and evaluate land plots intelligently.

Users can search for plots, explore detailed property insights, and receive AI-driven recommendations based on their preferences.

## Features

- Search and filter plots by location, price, and size  
- Detailed plot pages with amenities and nearby landmarks  
- AI-powered recommendations based on user queries  
- Shortlist/save favorite plots  
- Fast and responsive UI  

## Tech Stack

Frontend: Next.js, TypeScript, Tailwind CSS  
Backend: FastAPI (Python)  
Database: PostgreSQL + pgvector  
AI: Anthropic API
Infrastructure: Docker  

## Architecture
```text
Next.js (Frontend)
        ↓
FastAPI (Backend APIs + AI logic)
        ↓
PostgreSQL (Structured Data)
        ↓
pgvector (Semantic Search / RAG)
```

## Getting Started

Prerequisites:
- Python (3.10+)  
- Docker  

1. Clone the repository

git clone https://github.com/SwarnaMadhuriP/smartplots.git
cd smartplots  

2. Set up environment variables

cp .env.example .env
Update .env:
Paste your API Key

3. Start the database

docker compose up -d  

4. Set up backend

uv venv  
source .venv/bin/activate  
uv pip install fastapi uvicorn sqlalchemy 'psycopg[binary]' python-dotenv  

6. Run backend server

cd backend  
uvicorn app.main:app --reload  

6. Access the app

Backend API: http://127.0.0.1:8000  
API Docs: http://127.0.0.1:8000/docs  


## Future Improvements

- RAG-based semantic search using pgvector  
- Agentic workflows for dynamic recommendations  
- Map integration  
- Investment scoring for plots  
- User authentication  

## Why this project?

This project explores AI-driven decision-making in real estate by combining structured data with LLM-powered recommendations.
