"""
CivicFlow Backend — Startup Entry Point
========================================
Run this file from the `backend/` directory:

    python run.py

Or equivalently with uvicorn (recommended for production):

    uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

This wrapper ensures `backend/` is on sys.path so all
`from app.xxx import ...` absolute imports resolve correctly,
regardless of which directory you launch the process from.
"""

import sys
import os

# Add the `backend/` directory to sys.path so `from app.xxx` works everywhere
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
