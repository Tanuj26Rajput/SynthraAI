# 🤖 SynthraAI - AI-Powered Research Assistant

SynthraAI is a sophisticated, modular research assistant that automates complex research workflows by orchestrating multiple AI agents in a graph-based pipeline. It combines **query planning**, **web search**, **source evaluation**, **iterative refinement**, and **report generation** into a seamless, interactive research experience.

The system is built on **LangGraph** for agent orchestration, **Google Gemini** for AI reasoning, **SerpAPI** for search, and **MongoDB** for session persistence. It provides both a **CLI interface** for interactive research and **FastAPI endpoints** for programmatic access.

---

## 🎯 Project Vision

SynthraAI transforms how researchers gather and synthesize information. Instead of manually searching, evaluating, and organizing sources, SynthraAI:

1. **Plans** research by breaking complex queries into focused subtopics
2. **Searches** the web comprehensively across all subtopics
3. **Ranks** sources by credibility, recency, and relevance
4. **Critiques** research quality and identifies gaps
5. **Refines** queries based on critical feedback
6. **Synthesizes** findings into structured, professional reports

The entire process is **interactive**—users can approve results at any stage or request refinement for deeper investigation.

---

## ✨ Key Features

### 🧠 Multi-Agent Architecture
- **Planner Agent**: Decomposes research queries into 4-6 focused subtopics
- **Search Agent**: Performs distributed web searches across all subtopics using SerpAPI
- **Ranking Tool**: Scores sources by credibility (domain), recency, and relevance
- **Critic Agent**: Evaluates research sufficiency, identifies bias, and spots missing perspectives
- **Refiner Agent**: Improves queries based on critical feedback
- **Writer Agent**: Generates professional, structured research reports

### 📊 Graph-Based Orchestration
- **LangGraph** powers the workflow orchestration
- Deterministic state transitions and node sequencing
- Timeline tracking of all processing steps
- Composable, reusable agents

### 💾 Session Persistence
- **MongoDB** stores research sessions with full state snapshots
- Resume interrupted research from any checkpoint
- Maintain history for context-aware refinements
- Query auditing and traceability

### 🎮 Dual Interface
- **CLI Mode**: Interactive terminal experience for exploratory research
- **API Mode**: FastAPI endpoints for web/mobile client integration
- Streamlit UI layer (optional) for graphical interface

### ♻️ Iterative Refinement
- User-guided approval/rejection at critique stage
- Automatic query improvement based on critical feedback
- Configurable refinement loop limits (prevent infinite loops)
- Context retained across refinement iterations

---

## 📁 Repository Structure

```
SynthraAI/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── cli.py                  # Interactive CLI runner
│   │
│   ├── graph/
│   │   ├── builder.py          # LangGraph workflow construction
│   │   └── state.py            # GraphState Pydantic data model
│   │
│   ├── agents/
│   │   ├── planner.py          # Query → subtopic decomposition
│   │   ├── search.py           # Web search via SerpAPI
│   │   ├── critic.py           # Research quality evaluation
│   │   ├── refiner.py          # Query improvement logic
│   │   └── writer.py           # Report generation
│   │
│   ├── tools/
│   │   └── ranking.py          # Source ranking algorithm
│   │
│   ├── memory/
│   │   ├── memory.py           # MongoDB session persistence
│   │   └── session_store.py    # Session model definitions
│   │
│   └── routes/
│       └── research.py         # FastAPI endpoint handlers
│
├── ui/
│   └── streamlit.py            # Streamlit dashboard UI (optional)
│
├── README.md                   # This file
├── requirements.txt            # Python dependencies
└── .env                        # Configuration (create manually)
```

---

## ⚙️ Architecture & Data Flow

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INPUT                               │
│                     (Query + Session ID)                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │   1. LOAD MEMORY NODE      │
    │  (Retrieve past context)   │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │   2. PLANNER AGENT         │
    │  Query → 4-6 Subtopics     │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │   3. SEARCH AGENT          │
    │  Subtopics → Web Results   │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │   4. RANKING NODE          │
    │  Score & Sort Results      │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │   5. CRITIC AGENT          │
    │  Evaluate Quality & Gaps   │
    └────────────┬───────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ USER DECISION │
         ├───────────────┤
         │  Approve ────→ Writer Agent → Final Report
         │       or      │
         │  Refine ──────→ Refiner Agent → Improved Query → (Loop)
         └───────────────┘
```

### GraphState Data Model

The `GraphState` Pydantic model is the central state container flowing through all agents:

```python
class GraphState(BaseModel):
    query: str                              # Current research query
    plan: List[str] = []                    # Subtopic breakdown
    search_results: List[Dict[str, Any]] = []  # Raw search results from SerpAPI
    ranked_sources: List[Dict[str, Any]] = []  # Ranked, scored sources
    critique: str = ""                      # Critic's evaluation
    refinement_count: int = 0               # Number of refinements applied
    approved: bool = False                  # Final approval status
    final_report: str = ""                  # Generated research report
    history: List[Dict[str, Any]] = []      # Past session records
    session_id: str = ""                    # Unique session identifier
    timeline: list = []                     # Processing step log
```

---

## 🔧 Agent Details

### 1. **Planner Agent** (`app/agents/planner.py`)

**Purpose**: Decompose a research query into focused subtopics

**Input**: 
- `state.query` - User research query
- `state.history` - Previous queries (for context)

**Process**:
1. Call Gemini with a prompt to generate 4-6 subtopics
2. Parse response into a list of focused research areas
3. Include historical context to avoid redundant queries

**Output**:
```python
{
    "plan": ["Subtopic 1", "Subtopic 2", "Subtopic 3", ...],
    "timeline": state.timeline + ["🧠 Planner: Generated research plan"]
}
```

**Example**:
- Query: `"Effects of climate change on agriculture"`
- Plan: 
  - Climate patterns and CO2 levels
  - Crop yield impacts by region
  - Soil degradation trends
  - Water availability and drought patterns
  - Sustainable adaptation strategies

---

### 2. **Search Agent** (`app/agents/search.py`)

**Purpose**: Execute web searches for each subtopic and aggregate results

**Input**: 
- `state.plan` - List of subtopics to search

**Process**:
1. Iterate through up to 3 subtopics (configurable limit)
2. For each topic, call SerpAPI's Google Search wrapper
3. Extract organic results and normalize to title/URL/snippet format
4. Limit to 5 results per topic (configurable)
5. Deduplicate if necessary

**Output**:
```python
{
    "search_results": [
        {
            "title": "Article Title",
            "url": "https://example.com/article",
            "snippet": "Preview text..."
        },
        ...
    ],
    "timeline": state.timeline + [f"🌐 Search: Found {len(results)} results"]
}
```

**Limitations**:
- Respects SerpAPI rate limits
- Only top 5 results per subtopic to control volume
- Domain-based snippets only (no full content scraping)

---

### 3. **Ranking Tool** (`app/tools/ranking.py`)

**Purpose**: Score and rank sources by credibility, recency, and relevance

**Algorithm**:
```
score = (credibility × 0.5) + (recency × 0.3) + (relevance × 0.2)

credibility: 
  - 0.9 for .gov domains
  - 0.6 for other domains
  
recency:
  - 0.8 (constant, refined in future versions)
  
relevance:
  - 0.7 (constant, refined via snippet analysis)
```

**Output**: Same search results array, sorted by score descending

**Future Improvements**:
- Entity recognition to compute relevance from snippets
- Temporal metadata extraction for actual recency scoring
- Domain reputation awareness (academic, news, blog, etc.)

---

### 4. **Critic Agent** (`app/agents/critic.py`)

**Purpose**: Evaluate research sufficiency and identify gaps

**Input**: 
- `state.ranked_sources` - Top 5 ranked sources

**Process**:
1. Pass sources to Gemini with evaluation criteria
2. Ask Gemini to assess:
   - **Sufficiency**: Is data comprehensive enough?
   - **Bias**: Are perspectives balanced?
   - **Gaps**: What important perspectives are missing?
3. Return decision: `APPROVED` or `REVISE + reason`

**Output**:
```python
{
    "critique": "APPROVED" or "REVISE: Missing perspectives on X, potential bias toward Y",
    "awaiting_approval": True,
    "timeline": state.timeline + ["🧐 Critic: Evaluated research quality"]
}
```

**User Interaction**:
- User reviews critique and top 5 sources
- User decides: `approve` (proceed to writing) or `refine` (improve query)

---

### 5. **Refiner Agent** (`app/agents/refiner.py`)

**Purpose**: Improve the research query based on critical feedback

**Input**: 
- `state.query` - Current query
- `state.critique` - Critic's evaluation

**Process**:
1. Pass original query + critique to Gemini
2. Prompt Gemini to improve query specificity, clarity, and completeness
3. Address identified gaps and biases
4. Increment refinement counter

**Output**:
```python
{
    "query": "Improved, more specific research query",
    "refinement_count": state.refinement_count + 1,
    "timeline": state.timeline + ["🔁 Refiner: Improved query"]
}
```

**Example**:
- Original: `"Effects of climate change on agriculture"`
- Critique: `"REVISE: Missing crop-specific data, need regional focus"`
- Refined: `"Regional impacts of climate change on wheat and corn production in the US Midwest, including drought patterns and adaptive strategies"`

**Loop Control**:
- Maximum of 2 refinements before forcing final report
- Prevents infinite refinement loops

---

### 6. **Writer Agent** (`app/agents/writer.py`)

**Purpose**: Transform research data into a professional, structured report

**Input**: 
- `state.ranked_sources` - Top 3 sources (title, URL, snippet)
- `state.query` - Original research query

**Process**:
1. Format sources into readable summary with citations
2. Prompt Gemini to generate complete report with:
   - Professional structure (title, executive summary, etc.)
   - Clear headings and bullet points
   - All sections completed (no truncation)
   - Proper references
3. Enforce quality via explicit requirements

**Report Structure**:
```
1. Title (derived from query)
2. Executive Summary (key findings at a glance)
3. Introduction (context and methodology)
4. Key Findings (main discoveries)
5. Analysis (deeper interpretation)
6. Conclusion (synthesis and implications)
7. References (cited sources with URLs)
```

**Output**:
```python
{
    "final_report": "Complete formatted research report...",
    "timeline": state.timeline + ["✍️ Writer: Generated final report"]
}
```

**Quality Features**:
- Fallback to "fallback" string if generation fails
- Gemini error handling with exception logging
- Structured formatting enforced via prompt

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.10+**
- **MongoDB** (local or cloud)
- API keys for:
  - **Google Gemini** (via Google AI Studio)
  - **SerpAPI** (for Google Search)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/SynthraAI.git
cd SynthraAI
```

### Step 2: Create Python Environment

```bash
# Using venv
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n synthra python=3.10
conda activate synthra
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies**:
- `google-genai` - Google Gemini API client
- `langchain-community` - SerpAPI wrapper
- `pymongo` - MongoDB driver
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `streamlit` - UI framework (optional)
- `python-dotenv` - Environment variable management

### Step 4: Configure MongoDB

**Option A: Local MongoDB**
```bash
# Windows
net start MongoDB

# macOS (Homebrew)
brew services start mongodb-community

# Linux (systemd)
sudo systemctl start mongod
```

Verify connection:
```bash
mongosh  # Connect to mongodb://localhost:27017/
```

**Option B: MongoDB Atlas (Cloud)**
Update connection string in `app/memory/memory.py`:
```python
client = MongoClient("mongodb+srv://user:password@cluster.mongodb.net/")
```

### Step 5: Set Up Environment Variables

Create `.env` file in project root:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# SerpAPI for Google Search
SERPAPI_API_KEY=your_serpapi_api_key_here

# Optional: MongoDB connection (if not local)
MONGODB_URI=mongodb://localhost:27017/
```

**Getting API Keys**:

1. **Gemini API**:
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create new API key
   - Copy to `.env` as `GEMINI_API_KEY`

2. **SerpAPI**:
   - Register at [SerpAPI](https://serpapi.com)
   - Copy API key from dashboard
   - Add as `SERPAPI_API_KEY`

### Step 6: Verify Setup

Test imports and connections:

```bash
python -c "from app.graph.builder import build_graph; print('✓ Imports OK')"
```

---

## 💻 Usage Guide

### Option 1: CLI Mode (Interactive)

Best for exploratory research and decision-making.

**Start CLI**:
```bash
python -m app.cli
```

**CLI Features**:
- Session ID shown for resumption
- Real-time progress indicators (🧠, 🌐, 📊, 🧐, ✍️)
- Source preview before approval
- Refinement loop control

---

### Option 2: API Mode (Programmatic)

Best for web/mobile clients, automation, and integration.

**Start Server**:
```bash
uvicorn app.main:app --reload --port 8000
```

Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Endpoints**:

#### 1. **One-Shot Research**
```
POST /research?query=<query>&session_id=<optional>
```

**Request**:
```bash
curl -X POST "http://localhost:8000/research?query=Latest+AI+trends+2024"
```

**Response** (200):
```json
{
  "session_id": "uuid-string",
  "result": {
    "query": "Latest AI trends 2024",
    "plan": [...],
    "search_results": [...],
    "ranked_sources": [...],
    "critique": "...",
    "final_report": "...",
    "timeline": ["🧠 Planner: ...", "🌐 Search: ...", ...],
    "approved": true
  }
}
```

---

#### 2. **Start Interactive Session**
```
POST /research/start?query=<query>&session_id=<optional>
```

**Request**:
```bash
curl -X POST "http://localhost:8000/research/start?query=Climate+change+impacts"
```

**Response** (200):
```json
{
  "session_id": "uuid-string",
  "critique": "Research shows gaps in regional analysis...",
  "sources": [
    {
      "title": "Source Title",
      "url": "https://example.com",
      "snippet": "Preview text...",
      "score": 0.75
    },
    ...
  ],
  "message": "Approve or refine?"
}
```

**Returns**:
- Session ID for continuation
- Critique from critic agent
- Top 5 sources with scores
- Awaiting user decision

---

#### 3. **Continue Research**
```
POST /research/continue?session_id=<id>&decision=<approve|refine>
```

**Request**:
```bash
curl -X POST "http://localhost:8000/research/continue?session_id=uuid-string&decision=approve"
```

**Response if `approve`** (200):
```json
{
  "session_id": "uuid-string",
  "final_report": "Complete research report...",
  "approved": true,
  "ranking_sources": [...],
  "timeline": [...]
}
```

**Response if `refine`** (200):
```json
{
  "session_id": "uuid-string",
  "query": "Improved, more specific query",
  "plan": [...],
  "ranked_sources": [...],
  "critique": "Updated critique with refined data...",
  "refinement_count": 1,
  "timeline": [...]
}
```

**Refinement Loop**:
- Returns new critique + sources for user review
- User can approve again or refine further
- Auto-stops at 2 refinements

---

### Option 3: Streamlit UI (Optional)

For a graphical web interface:

```bash
streamlit run ui/streamlit.py
```

Opens browser at `http://localhost:8501`

**Features** (to be implemented):
- Query input form
- Live progress indicators
- Source preview table
- Critique display
- Approve/Refine buttons
- Final report markdown rendering
- Session history sidebar

---

## 📊 MongoDB Session Schema

Sessions are stored in MongoDB for full research auditability.

**Collection**: `synthra.sessions`

**Document Structure**:
```json
{
  "_id": ObjectId(...),
  "session_id": "uuid-string",
  "state": {
    "query": "Original research query",
    "plan": ["Topic 1", "Topic 2", ...],
    "search_results": [...],
    "ranked_sources": [...],
    "critique": "...",
    "final_report": "...",
    "history": [...],
    "refinement_count": 0,
    "timeline": [...]
  },
  "query": "Original research query",
  "plan": ["Topic 1", ...],
  "report": "Generated report text",
  "sources": [
    {
      "title": "...",
      "url": "...",
      "snippet": "...",
      "score": 0.75
    }
  ],
  "timestamp": ISODate("2024-04-05T10:30:00Z")
}
```
---

## 🔍 Configuration & Tuning

### Planner Agent
- **Subtopic count**: Currently 4-6, adjustable in `planner.py`
- **Context window**: Includes last 2 queries from history

### Search Agent
- **Topics per search**: Currently 3 (modify in `search_agent()`)
- **Results per topic**: Currently 5 (modifiable)
- **SerpAPI params**: Can add filters (date, region, etc.)

### Ranking Algorithm
```python
def rank_sources(results):
    for r in results:
        credibility = 0.9 if ".gov" in r["url"] else 0.6
        recency = 0.8  # Current placeholder
        relevance = 0.7  # Current placeholder
        
        score = (credibility × 0.5) + (recency × 0.3) + (relevance × 0.2)
```

**Tuning Ideas**:
- Extract publish date from snippet for real recency
- Use NLP for relevance matching to query
- Add academic domain boost (0.95 for .edu, .org research sites)

### Refinement Limits
- **Max refinements**: Currently 2 (in `cli.py` and `routes/research.py`)
- Prevents infinite loops while allowing improvement

### LLM Models
All agents use `gemini-2.5-flash`:
- Fast inference
- Cost-effective for production
- Consider `gemini-pro` for higher quality

**Gemini Parameters**:
- Temperature: 0.7 (creative but consistent)
- Adjustable per agent if needed

---

## 🛡️ Error Handling & Reliability

### Graceful Failures

**Gemini API Error**:
```python
def gemi_invoke(prompt: str) -> str:
    try:
        response = client_gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        if not response or not response.text:
            return "fallback"
        return response.text.strip()
    except Exception as e:
        print("Gemini API Error:", e)
        return "fallback"
```

**Fallbacks**:
- Gemini errors return `"fallback"` string
- SerpAPI errors return empty results
- MongoDB unavailability skipped (session saving fails gracefully)
---

## 📈 Performance Metrics

Each research cycle logs to MongoDB with timestamps.

**Typical Flow Duration**:
| Step | Avg Time |
|------|----------|
| Planner Agent | 3-5s |
| Search Agent | 5-8s |
| Ranking | <1s |
| Critic Agent | 3-5s |
| **Total Research** | **12-20s** |
| Refiner Agent (if refining) | 3-5s |
| Writer Agent (if approving) | 8-12s |

**Optimization Opportunities**:
- Parallelize subtopic searches
- Cache ranking computations
- Batch API calls to Gemini
- Implement result caching by query hash

---

## 🧪 Example Workflows

### Workflow 1: Simple Approval
```
User Query: "What is blockchain technology?"
    ↓
Planner: [History, Core concepts, Use cases, Security, Future]
    ↓
Search: 25 results across topics
    ↓
Rank & Critic: "✓ APPROVED - Comprehensive coverage"
    ↓
User: approve
    ↓
Writer: Professional report generated
```

### Workflow 2: Refinement Loop
```
User Query: "Effects of social media on teenagers"
    ↓
Planner: [General effects, Mental health, Academic impact, etc.]
    ↓
Search & Rank: 25 results
    ↓
Critic: "REVISE - Missing longitudinal studies, gender differences"
    ↓
User: refine
    ↓
Refiner: Query → "Effects of social media on teenager mental health 
          and academic performance: gender-specific longitudinal impacts"
    ↓
Planner (refined): [Mental health metrics, Academic outcomes, Gender gaps, etc.]
    ↓
Search & Rank: 25 new results
    ↓
Critic: "✓ APPROVED - Addresses all gaps"
    ↓
User: approve
    ↓
Writer: Report generated
```
---

## 📄 License

See LICENSE file in repository.

---

## 🎓 About

SynthraAI was created as a demonstration of modular, agentic AI workflows. It showcases how LangGraph orchestration, multi-turn LLM reasoning, and external tool integration can create powerful research automation.

Built for rapid prototyping. Ready for production enhancement.

**Questions?** Open an issue or discussion in the repository.

---

**Last Updated**: April 5, 2026  
**Status**: Active Development
