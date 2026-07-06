# SmartPlots

### AI-Powered Real Estate & Land Intelligence  
*Find Your Plot, Smarter.*

SmartPlots is an AI-powered real estate intelligence platform that helps users discover, analyze, and evaluate land plots. Navigating zoning ordinances, utility access, deed restrictions, and long-term appreciation is notoriously complex. SmartPlots combines structured database queries with a state-of-the-art **multi-agent AI pipeline** to deliver instant, customized real estate advice.

---

## 📸 Application Screenshots
*Note: Capture screenshots of your local application running at http://localhost:3000 and save them to the paths below to display them.*

### Discover Listings Dashboard
*Save screenshot to: `frontend/public/screenshots/discover_page.png`*
![Discover Dashboard](frontend/public/screenshots/discover_page.png)

### Conversational AI Advisor
*Save screenshot to: `frontend/public/screenshots/advisor_page.png`*
![AI Advisor](frontend/public/screenshots/advisor_page.png)

### Interactive Map Explorer
*Save screenshot to: `frontend/public/screenshots/map_page.png`*
![Map Explorer](frontend/public/screenshots/map_page.png)

---

## 🏗️ System Architecture

SmartPlots features four core intelligent workflows powered by FastAPI, PostgreSQL (pgvector), and Google ADK (Agent Development Kit).

```text
                        Next.js / TypeScript Frontend
                                      │
                         FastAPI Backend API Layer
      ┌───────────────────────┬───────┴───────────────┬──────────────────────┐
      ▼                       ▼                       ▼                      ▼
DiscoverPlots            Comparison               AI Advisor              HITL Loop
(Semantic Search)        (Side-by-Side)       (ADK Graph Workflow)     (Feedback Re-run)
      │                       │                       │                      │
      ▼                       ▼                       ▼                      ▼
pgvector Search          Gemini LLM             Parallel Panel         State Update
 (PostgreSQL)          (Structured JSON)      (4 Specialist Nodes)      (& Re-score)
```

### 🔍 1. DiscoverPlots (Semantic Search Pipeline)
Translates natural-language search queries into structured database queries combined with vector similarity search.
*   **Query Parsing**: The `ai_search_agent` takes the raw user query (e.g. *"wooded acreage in WA with road access"*) and extracts structured attributes.
*   **Vector Database Search**: Leverages PostgreSQL + `pgvector` to run a cosine-similarity query across plot descriptions alongside hard filters.
*   **Ranking Explanation**: The `ai_search_ranking_explainer_agent` takes the top results and writes a concise natural-language explanation explaining *why* they were matched and ranked.

### 📊 2. Comparison Engine
Enables side-by-side analysis of multiple plots against a user's specified goal.
*   **Data Aggregation**: Standardizes and formats multiple plot attributes (acres, pricing, road access, utilities, and known risks) into a unified text block.
*   **Structured Analysis**: Invokes Gemini (`gemini-2.5-flash`) with a strict schema constraint (`ComparisonResponse`).
*   **Outputs**: Assigns custom "awards" to each plot (e.g. *"Lowest Risk"* or *"Best Value"*) and provides a detailed breakdown of pros and cons relative to the user's specific goals.

### 🧠 3. AI Advisor
Goal-based land evaluation routing through a directed-graph state machine.
*   **Graph State**: Managed via a shared context object (`WorkflowState`) passed sequentially through processing nodes.
*   **Scoring & RAG**: Filters and scores the catalog in Python before executing document semantic search (RAG) against PDF brochures and utility records.
*   **Dynamic Router**:
    *   **Fast Path**: Directly returns a recommendation if there is a clear, high-scoring winner with a large gap and no notices.
    *   **Specialist Path (Multi-Agent Panel)**: For close or complex matches, it triggers specialized analysis nodes:
        *   *Investment Node*: Scores appreciation, price per acre, and budget fit.
        *   *Risk Node*: Scores zoning, utilities, and flooding hazards.
        *   *Location Node*: Evaluates accessibility and purpose suitability.
        *   *Document Intelligence Node*: Extracts relevant zoning and deed facts from raw PDFs.
*   **Synthesis**: Enriches the Gemini prompt with the active specialist reports to generate the final recommendation.

### 🔄 4. Human-in-the-Loop (HITL) Feedback Loop
Enables conversational preference adjustment and interactive recommendation refinement.
*   **Feedback Mapping**: Translates user corrections (e.g., *"This is too expensive"* or *"I need electricity"* ) into updated query constraints.
*   **Workflow Re-entry**: Session states are updated in the database, and a refinement workflow is triggered.
*   **Forced Specialist Route**: Refinement passes are routed strictly through the **Specialist Path** to re-analyze alternatives carefully and detail the tradeoffs of the new recommendation.

---

## 🛠️ Tech Stack

*   **Frontend**: Next.js (TypeScript), Tailwind CSS, Leaflet Maps
*   **Backend**: FastAPI (Python), SQLAlchemy, PostgreSQL + `pgvector`
*   **AI/LLM**: Google ADK (Agent Development Kit), Gemini 2.5 Flash

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed locally:
*   [Docker](https://www.docker.com/)
*   [Python 3.10+](https://www.python.org/downloads/)
*   [Node.js 18+](https://nodejs.org/)

---

### Step 1: Clone the Repository & Configure Environment

1. Clone the project:
   ```bash
   git clone https://github.com/SwarnaMadhuriP/smartplots.git
   cd smartplots
   ```
2. Configure your environment variables:
   ```bash
   cp .env.example .env
   ```
3. Open the `.env` file and insert your Gemini API Key:
   ```env
   GEMINI_API_KEY=your-actual-gemini-api-key
   ```

---

### Step 2: Spin Up the PostgreSQL Database

Start the database container (includes the `pgvector` extension):
```bash
docker compose up -d
```

---

### Step 3: Run the Backend API

1. Navigate to the backend directory and set up a virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the database migrations & seed scripts:
   *   **Seed listings**:
       ```bash
       python seed/seed_plots.py
       ```
   *   **Ingest documents for RAG (vector store embeddings)**:
       ```bash
       python seed/ingest_plot_documents.py
       ```
4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
   *   *Backend API runs at: http://localhost:8000*
   *   *Swagger Docs: http://localhost:8000/docs*

---

### Step 4: Run the Frontend Application

1. Open a new terminal window and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   *   *Frontend app runs at: http://localhost:3000*
