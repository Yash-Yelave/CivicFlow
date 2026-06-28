# CivicFlow 🌐🏙️
> **Autonomous Municipal Triage System**

CivicFlow is an interactive platform that empowers citizens to identify, report, and track hyperlocal community issues (such as potholes, water leakages, and broken streetlights) while utilizing an AI multi-agent system to autonomously categorize, route, and analyze reports for municipal action.

---

## 📂 Repository Structure

The project is structured as follows:

```
civicflow/
│
├── frontend/                  # React (Vite) Application
│   ├── public/                # Static assets (favicon, etc.)
│   ├── src/
│   │   ├── assets/            # Images, icons, CSS
│   │   ├── components/        # Reusable UI (Map, IssueCard, UpvoteButton)
│   │   ├── pages/             # Main views (Dashboard, AdminAnalytics)
│   │   ├── services/          # API call logic (Axios config to FastAPI)
│   │   ├── App.jsx            # Main application router/layout
│   │   └── main.jsx           # React entry point
│   ├── .firebaserc            # Firebase project target configuration
│   ├── firebase.json          # Firebase Hosting rules and configuration
│   ├── package.json           # Frontend dependencies
│   └── vite.config.js         # Vite bundler configuration
│
├── backend/                   # FastAPI Application
│   ├── app/
│   │   ├── api/               # API endpoint routers (e.g., routes_reports.py)
│   │   ├── core/              # Configuration (Firebase init, CORS setup)
│   │   ├── models/            # Pydantic schemas (validating Gemini JSON)
│   │   ├── services/          # Business logic (Gemini agent chains, Firestore logic)
│   │   └── main.py            # FastAPI application entry point
│   ├── .env                   # API Keys (Google AI Studio, Firebase Admin) - DO NOT COMMIT
│   ├── .env.example           # Template for environment variables
│   ├── Dockerfile             # Instructions for Google Cloud Run containerization
│   └── requirements.txt       # Python dependencies
│
├── docs/                      # Project Documentation
│   ├── CivicFlow_Architecture.md
│   ├── Problem_Statement_Selected.md
│   ├── Solution_Overview.md
│   ├── Key_Features.md
│   ├── Technologies_Used.md
│   ├── Google_Technologies_Utilized.md
│   └── Hackathon_Submission.pdf (Placeholder/Guidance)
│
├── .gitignore                 # Ignore node_modules, venv, .env, etc.
└── README.md                  # Main entry point for repository visitors
```

---

## 🛠️ Quick Start

### Backend (FastAPI)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env` (copied from `.env.example`).
5. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend (React + Vite)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

---

# 🧠 AI Multi-Agent Triage Workflow
Powered by **Google AI Studio (Gemini 2.5 Flash)**:
1. **Agent 1: The Assessor (Vision AI)** - Examines the image uploaded by the citizen to classify the issue and severity in structured JSON using zero-cost Base64 compression.
2. **Agent 2: The Router (Workflow Automation)** - Takes the Assessor's JSON and determines the target municipal department, drafting a formal maintenance ticket.
3. **Agent 3: The Analyst (Predictive Insights & Event-Driven Analytics)** - Scans all Firestore reports to identify patterns and predict hotspots. Refactored into a high‑performance event‑driven cached architecture with asynchronous background generation (`analytics_cache/latest` & `analytics_metadata/state`), returning instant responses (<50ms) without blocking dashboard loads on LLM inference.
4. **Admin Refresh** – Trigger a cache regeneration via `POST /api/analytics/regenerate` to recompute analytics on demand.

Refer to the [Doc/](file:///d:/Hackathon_Projects/CivicFlow/Doc/) directory for detailed architecture and project definitions.