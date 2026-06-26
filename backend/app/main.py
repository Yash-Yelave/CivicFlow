import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="CivicFlow API",
    description="Autonomous Municipal Triage System Backend with Gemini Multi-Agent System",
    version="1.0.0"
)

# Set up CORS middleware to allow requests from the React frontend
origins = [
    "http://localhost:5173",  # Default Vite local URL
    "http://localhost:3000",
    "*"                       # Allow all for deployment testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "CivicFlow API",
        "agents": ["The Assessor (Vision)", "The Router (Workflow)", "The Analyst (Insights)"]
    }

# Ready for importing and registering routers
# from app.api import reports_router
# app.include_router(reports_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
