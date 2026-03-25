# SynthraAI

SynthraAI is a modular research assistant that combines planner, search, critic, refiner, and writer agents into a graph-based flow. It uses Google Gemini API for LLM tasks, SerpAPI for web search, and MongoDB for session persistence.

## ✅ Core Features

- Query-driven research pipeline
- Agent components:
  - `planner_agent` (break query into topics)
  - `search_agent` (fetch results from SerpAPI)
  - `critic_agent` (evaluate candidate sources)
  - `refinement_agent` (improve query from critique)
  - `writer_agent` (produce structured final report)
- Graph orchestration via `langgraph`
- Session store in MongoDB
- CLI in `app/cli.py` and FastAPI endpoints in `app/routes/research.py`

## 📁 Repository Structure

- `app/main.py` - FastAPI app entry point
- `app/cli.py` - Command-line research runner and loop
- `app/graph/builder.py` - Graph definition linking agents
- `app/graph/state.py` - `GraphState` Pydantic model
- `app/agents` - individual business logic functions
- `app/memory/memory.py` - MongoDB session save/load
- `app/routes/research.py` - API endpoints for web client
- `ui/streamlit.py` - optional UI layer (Streamlit)

## ⚙️ Requirements

- Python 3.10+
- MongoDB running locally (`mongodb://localhost:27017/`)
- `.env` config with keys:
  - `SERPAPI_API_KEY` (Google Search API wrapper)
  - `GEMINI_API_KEY` (Google Gemini multimodal model)

### Python dependencies

From `requirements.txt`:

- `google-search-results`
- `pymongo`
- `uuid`
- `fastapi`
- `langchain-google-genai`
- `streamlit`

Install:

```bash
pip install -r requirements.txt
```

## 🛠️ Setup

1. Clone repo and enter directory:

```bash
git clone <repo-url>
cd SynthraAI
```

2. Copy `.env.example` (if exists) or create `.env`:

```env
SERPAPI_API_KEY=your_serpapi_key
GEMINI_API_KEY=your_gemini_key
```

3. Run MongoDB locally:

```bash
# Windows (example)
net start MongoDB
```

## ▶️ Run CLI Flow

```bash
python -m app.cli
```

CLI flow:
1. Enter research query
2. Compare critique/sources
3. Input `approve` / `refine`
4. On `approve` final report prints

## ▶️ Run API Server

```bash
uvicorn app.main:app --reload
```

Endpoints:

- `POST /research` — one-step research + session save
- `POST /research/start` — start session, returns critique + sources
- `POST /research/continue` — continue with `decision=approve|refine`

## 🧠 Architecture

1. `build_graph()` sets up nodes and edges in `app/graph/builder.py`.
2. `GraphState` carries query, plan, sources, critique, history, and flags.
3. Sequencing: load memory -> planner -> search -> ranking -> critic -> end
4. `planner` calls Gemini to split query into sub-topics.
5. `search` uses SerpAPI results and returns top entries.
6. `ranking` sorts sources (in `app/tools/ranking.py`).
7. `critic` rate quality; user can refine and rerun.
8. `writer` writes a full report via Gemini.

## 🧩 FastAPI / Reinforcement

- `app/routes/research.py` persists state with `save_sessions`.
- `load_last_state` uses most recent Mongo session for continue.

## 🐛 Common Issues

- **No MongoDB**: Ensure MongoDB container or service running.
- **API keys**: Missing or invalid keys cause Serp/API calls to fail.
- **Rate limits**: Both Gemini and SerpAPI have quota limits.

## 🛡️ Security and safety

- LLM failure fallback returns `"fallback"` and prints exceptions.
- No production-level input validation yet; recommended to add.

## 📌 Next improvements

- Add `app/tools/ranking.py` algorithm tuning (currently first-pass).
- Implement `ui/streamlit.py` interactive frontend.
- Add tests for graph transitions and state persistence.
- Add authentication and rate-limiting on API endpoints.

---

Made for rapid research prototyping with LLM + search integration.
