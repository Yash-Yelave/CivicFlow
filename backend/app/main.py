"""
CivicFlow Backend — Application Entry Point (main.py)
=======================================================
FastAPI application factory:
  - Configures CORS middleware for React frontend communication
  - Registers all API routers
  - Provides a health-check root endpoint
  - Launches Uvicorn when run directly
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env file for local development (GEMINI_API_KEY, FIREBASE_*, etc.)
load_dotenv()

# Configure structured logging for readability in terminal and Cloud Run logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("civicflow")

# ---------------------------------------------------------------------------
# FastAPI Application Instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="CivicFlow API",
    description=(
        "Autonomous Municipal Triage System — Backend API\n\n"
        "**Agents:**\n"
        "- 🔍 **Agent 1 (Assessor):** Visual infrastructure classification via Gemini Vision\n"
        "- 🗺️  **Agent 2 (Router):** Automated municipal department routing\n"
        "- 📊 **Agent 3 (Analyst):** Predictive pattern intelligence from aggregated data"
    ),
    version="1.0.0",
    docs_url="/docs",        # Swagger UI at http://localhost:8080/docs
    redoc_url="/redoc"       # ReDoc UI at http://localhost:8080/redoc
)

# ---------------------------------------------------------------------------
# CORS Middleware
# Configured to allow all origins so the local Vite dev server (port 5173)
# and any deployed frontend can communicate without CORS preflight failures.
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],          # Allow GET, POST, PATCH, OPTIONS, etc.
    allow_headers=["*"],          # Allow Content-Type, Authorization, etc.
)

# ---------------------------------------------------------------------------
# Register API Routers
# ---------------------------------------------------------------------------

# Import here (after app is created) to avoid circular import issues
# Firebase and Gemini SDKs initialize when services are first imported
from app.api.routes import router as api_router

app.include_router(api_router)

logger.info("🚀 CivicFlow API router registered. Multi-agent pipeline ready.")

# ---------------------------------------------------------------------------
# Health Check Root Endpoint
# ---------------------------------------------------------------------------

@app.get(
    "/",
    tags=["Health"],
    summary="Service health check",
    description="Returns the service status and active agent list."
)
async def root():
    """Simple health-check used by Cloud Run and load balancers."""
    return {
        "status": "healthy",
        "service": "CivicFlow — Autonomous Municipal Triage System",
        "version": "2.0.0",
        "agents": {
            "agent_1": "The Assessor (Vision AI — Gemini 2.5 Flash)",
            "agent_2": "The Router (Municipal Dispatcher — Gemini 2.5 Flash)",
            "agent_3": "The Analyst (Predictive Intelligence — Gemini 2.5 Flash, cached)"
        },
        "endpoints": {
            "POST /api/report":                    "Submit new infrastructure issue",
            "GET  /api/tickets":                   "Fetch all active tickets (map feed)",
            "PATCH /api/tickets/{id}/verify":      "Community upvote a ticket",
            "GET  /api/analytics":                 "Read cached Agent 3 analytics (~50ms, non-blocking)",
            "POST /api/analytics/regenerate":      "Force-invalidate cache and trigger background refresh"
        },
        "analytics_architecture": {
            "cache_collection":    "analytics_cache/latest",
            "metadata_collection": "analytics_metadata/state",
            "invalidation":        "Event-driven — triggered automatically on ticket mutations",
            "worker":              "FastAPI BackgroundTasks — non-blocking, never delays responses"
        }
    }


# ---------------------------------------------------------------------------
# Local Development Entry Point
# Run with: python app/main.py   OR   uvicorn app.main:app --reload
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,         # Hot-reload on file changes (dev only)
        log_level="info"
    )
