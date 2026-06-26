"""
CivicFlow Backend — API Routes
================================
All FastAPI route handlers for the CivicFlow multi-agent triage platform.

Endpoints:
  POST   /api/report              — Submit a new issue (triggers Agent 1 + 2 pipeline)
  GET    /api/tickets             — Fetch all active tickets for the live map feed
  PATCH  /api/tickets/{id}/verify — Community upvote (increment verification counter)
  GET    /api/analytics           — Trigger Agent 3 for predictive dashboard insights
"""

import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse

from app.services import firebase_service, gemini_service

logger = logging.getLogger(__name__)

# Create a namespaced router — all routes here will be prefixed with /api
router = APIRouter(prefix="/api", tags=["CivicFlow Core API"])


# ---------------------------------------------------------------------------
# POST /api/report
# The Core Multi-Agent Pipeline: Image Upload → Agent 1 → Agent 2 → Firestore
# ---------------------------------------------------------------------------

@router.post(
    "/report",
    summary="Submit a new infrastructure issue report",
    description=(
        "Accepts a citizen's uploaded image and location data. Triggers the full "
        "multi-agent AI pipeline: Agent 1 classifies the image, Agent 2 routes it "
        "to the correct department, and the result is persisted in Firestore."
    ),
    status_code=status.HTTP_201_CREATED
)
async def submit_report(
    image: UploadFile = File(..., description="Photo of the infrastructure issue"),
    latitude: float   = Form(..., description="GPS latitude of the issue"),
    longitude: float  = Form(..., description="GPS longitude of the issue"),
    description: Optional[str] = Form(None, description="Optional user-provided description")
):
    """
    Multi-Agent Pipeline Execution:

    Step A → Upload image to Firebase Storage → get public URL
    Step B → Agent 1 (Assessor): Visual classification via Gemini Vision
    Step C → Agent 2 (Router): Department routing based on Agent 1 output
    Step D → Compile full ticket document
    Step E → Save to Firestore `tickets` collection
    """
    logger.info(f"📥 New report received at ({latitude}, {longitude})")

    # ------------------------------------------------------------------
    # Step A: Read image bytes and upload to Firebase Storage
    # ------------------------------------------------------------------
    try:
        image_bytes = await image.read()
        content_type = image.content_type or "image/jpeg"

        image_url = await firebase_service.upload_image_to_storage(
            image_bytes=image_bytes,
            original_filename=image.filename or "upload.jpg",
            content_type=content_type
        )
    except Exception as e:
        logger.error(f"❌ Firebase Storage upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {str(e)}"
        )

    # ------------------------------------------------------------------
    # Step B: Agent 1 — The Assessor (Vision AI via Gemini Flash)
    # Sends raw image bytes + MIME type for visual analysis
    # ------------------------------------------------------------------
    try:
        agent1_result = await gemini_service.run_agent1_assessor(
            image_bytes=image_bytes,
            content_type=content_type
        )
    except Exception as e:
        logger.error(f"❌ Agent 1 (Assessor) failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent 1 (Visual Assessment) failed: {str(e)}"
        )

    # ------------------------------------------------------------------
    # Step C: Agent 2 — The Router (Municipal Dispatcher)
    # Receives Agent 1's structured Pydantic model as input
    # ------------------------------------------------------------------
    try:
        agent2_result = await gemini_service.run_agent2_router(
            assessment=agent1_result
        )
    except Exception as e:
        logger.error(f"❌ Agent 2 (Router) failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent 2 (Routing) failed: {str(e)}"
        )

    # ------------------------------------------------------------------
    # Step D: Compile the full ticket document
    # Merges: location + image + user description + Agent 1 + Agent 2
    # ------------------------------------------------------------------
    ticket_data = {
        "image_url":         image_url,
        "latitude":          latitude,
        "longitude":         longitude,
        "description":       description or "",
        "status":            "Pending",
        "upvotes":           1,
        # Store agent outputs as plain dicts for flexible Firestore storage
        "agent1_assessment": agent1_result.model_dump(),
        "agent2_routing":    agent2_result.model_dump(),
    }

    # ------------------------------------------------------------------
    # Step E: Save to Firestore and return the new ticket to the frontend
    # ------------------------------------------------------------------
    try:
        ticket_id, saved_ticket = firebase_service.create_ticket(ticket_data)
    except Exception as e:
        logger.error(f"❌ Firestore write failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database write failed: {str(e)}"
        )

    logger.info(f"🎉 Report pipeline complete. Ticket ID: {ticket_id}")
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "message": "Report successfully processed by the AI triage system.",
            "ticket_id": ticket_id,
            "ticket": saved_ticket
        }
    )


# ---------------------------------------------------------------------------
# GET /api/tickets
# Fetch all active triage tickets for the Leaflet map feed
# ---------------------------------------------------------------------------

@router.get(
    "/tickets",
    summary="Retrieve all active infrastructure tickets",
    description="Returns all triage ticket documents from Firestore for display on the live map."
)
async def get_tickets():
    """
    Fetches the entire `tickets` collection from Firestore.
    Each ticket includes the document ID, location, AI assessment, status, and upvote count.
    """
    try:
        tickets = firebase_service.get_all_tickets()
    except Exception as e:
        logger.error(f"❌ Failed to fetch tickets from Firestore: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tickets: {str(e)}"
        )

    return {
        "success": True,
        "count": len(tickets),
        "tickets": tickets
    }


# ---------------------------------------------------------------------------
# PATCH /api/tickets/{ticket_id}/verify
# Community upvote — atomically increments the `upvotes` field in Firestore
# ---------------------------------------------------------------------------

@router.patch(
    "/tickets/{ticket_id}/verify",
    summary="Upvote / verify an existing issue report",
    description=(
        "Allows community members to validate a reported issue. "
        "Atomically increments the ticket's upvote counter in Firestore."
    )
)
async def verify_ticket(ticket_id: str):
    """
    Uses Firestore's server-side Increment to safely handle concurrent upvotes
    without race conditions or stale reads.
    """
    try:
        new_count = firebase_service.increment_ticket_upvotes(ticket_id)
    except ValueError as e:
        # Ticket not found in Firestore
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Upvote failed for ticket '{ticket_id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )

    return {
        "success": True,
        "ticket_id": ticket_id,
        "new_upvote_count": new_count
    }


# ---------------------------------------------------------------------------
# GET /api/analytics
# Agent 3 — Predictive Intelligence Dashboard
# ---------------------------------------------------------------------------

@router.get(
    "/analytics",
    summary="Generate AI-powered predictive infrastructure analytics",
    description=(
        "Triggers Agent 3 (The Analyst) to analyze all accumulated tickets "
        "for systemic patterns, risk clusters, and preventative recommendations."
    )
)
async def get_analytics():
    """
    Full Agent 3 Pipeline:
    1. Fetch all Firestore tickets
    2. Condense into a readable summary (handled in gemini_service)
    3. Pass to Gemini Flash for pattern analysis
    4. Return structured JSON for the analytics dashboard
    """
    # Step 1: Fetch the raw ticket data from Firestore
    try:
        tickets = firebase_service.get_all_tickets()
    except Exception as e:
        logger.error(f"❌ Failed to fetch tickets for analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch ticket data: {str(e)}"
        )

    # Step 2 + 3: Run Agent 3 (The Analyst) with the ticket dataset
    try:
        analytics_result = await gemini_service.run_agent3_analyst(tickets)
    except Exception as e:
        logger.error(f"❌ Agent 3 (Analyst) failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent 3 (Analytics) failed: {str(e)}"
        )

    return {
        "success": True,
        "ticket_count_analyzed": len(tickets),
        "analytics": analytics_result.model_dump()
    }
