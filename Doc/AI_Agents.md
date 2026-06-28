# CivicFlow AI Agents

CivicFlow leverages a sequential multi-agent architecture powered by Google AI Studio (Gemini 2.5 Flash). By chaining specialized agents with strict Pydantic JSON schemas, the system replaces manual forms and complex dropdowns with automated intelligence.

---

## Agent 1: The Assessor (Vision AI)

**Role**: Initial intake and classification of visual evidence.

- **Responsibilities**: Analyze the citizen's uploaded photo to identify the anomaly, assign a severity score, and generate a brief summary.
- **Inputs**: Base64 encoded image string, optional text description from the user.
- **Outputs** (JSON):
  - `category` (e.g., Infrastructure, Sanitation, Utility, Traffic, Other)
  - `severity` (e.g., Low, Medium, High, Critical)
  - `summary` (e.g., "Large pothole in center lane")
- **Prompt Strategy**: The Assessor is instructed to act as a strict municipal inspector. It looks for public safety hazards and ignores irrelevant background objects.
- **Failure Handling**: If the image is unrecognizable or lacks a civic issue, the agent defaults to `category: Other` and `severity: Low` with a summary indicating manual review is needed.

---

## Agent 2: The Router (Workflow Automation)

**Role**: Departmental assignment and triage.

- **Responsibilities**: Take the output of the Assessor and determine which municipal department should own the ticket. Assign an actionable priority level.
- **Inputs**: The structured JSON output from Agent 1, plus geolocation coordinates (Lat/Lng).
- **Outputs** (JSON):
  - `department` (e.g., Public Works, Sanitation, Water Authority)
  - `priority` (e.g., P1, P2, P3, P4)
  - `recommended_action` (e.g., "Dispatch repair crew to patch asphalt")
- **Prompt Strategy**: The Router is given a list of predefined municipal departments and strict rules for priority mapping (e.g., Water Leaks = P1, Graffitti = P4).
- **Validation**: Enforced via `Agent2Routing` Pydantic schema in FastAPI.

---

## Agent 3: The Analyst (Event-Driven Predictive Analytics)

**Role**: Macro-level predictive insights and risk clustering.

- **Responsibilities**: Analyze the aggregate dataset of all active tickets to identify geospatial hotspots, recurring issues, and provide preventative recommendations to city planners.
- **Inputs**: A minimized JSON array of all tickets in Firestore.
- **Outputs** (JSON):
  - `summary` (Overall city status)
  - `high_risk_clusters` (Array of named hotspots and their descriptions)
  - `preventative_recommendations` (Strategic long-term advice)

### Execution Model: Event-Driven Cached Architecture

Unlike Agents 1 and 2 which execute synchronously during a citizen's POST request, Agent 3 operates in the background:
1. **Trigger**: When a ticket is created or updated, `datasetVersion` increments.
2. **Worker**: FastAPI `BackgroundTasks` spawns an asynchronous worker.
3. **Locking**: The worker acquires an optimistic lock in `analytics_metadata/state` to prevent concurrent LLM executions.
4. **Cache Update Process**: Agent 3 executes against the Gemini API. Upon success, results are written to `analytics_cache/latest`.
5. **Dashboard Retrieval**: User requests to `GET /api/analytics` return the cached document in <50ms, bypassing the LLM entirely.

### Manual Refresh Endpoint
Administrators can invoke `POST /api/analytics/regenerate` to manually increment the `datasetVersion` and force the background worker to re-run Agent 3 immediately.
