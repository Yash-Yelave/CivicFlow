"""
CivicFlow Backend — API Routes
================================
All FastAPI route handlers for the CivicFlow multi-agent triage platform.

Endpoints:
  POST   /api/report                — Submit a new issue (triggers Agent 1 + 2 pipeline)
  GET    /api/tickets               — Fetch all active tickets for the live map feed
  PATCH  /api/tickets/{id}/verify   — Community upvote (increment verification counter)
  GET    /api/analytics             — Return cached Agent 3 analytics (non-blocking)
  POST   /api/analytics/regenerate  — Force-invalidate cache and trigger background refresh

Architecture note — GET /api/analytics:
  Old flow: request → fetch tickets → Agent 3 (Gemini) → response  (~5-15 s)
  New flow: request → read Firestore cache → response              (~50-200 ms)
            └─ if stale → enqueue BackgroundTask → Agent 3 runs asynchronously

  The dashboard NEVER waits for Gemini. The response always includes a
  `cache_status` field so the frontend can show a "Refreshing..." indicator
  when stale data is being updated in the background.
"""

import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse

from app.services import firebase_service, gemini_service, image_service
from app.services.analytics_service import analytics_service

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
        "to the correct department, and the result is persisted in Firestore. "
        "After the ticket is saved, a background analytics refresh is enqueued "
        "so the dashboard reflects the new data as soon as possible."
    ),
    status_code=status.HTTP_201_CREATED
)
async def submit_report(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(..., description="Photo of the infrastructure issue"),
    latitude: float   = Form(..., description="GPS latitude of the issue"),
    longitude: float  = Form(..., description="GPS longitude of the issue"),
    description: Optional[str] = Form(None, description="Optional user-provided description")
):
    """
    Multi-Agent Pipeline Execution:

    Step A → Compress image and convert to Base64 (Zero-Cost Architecture)
    Step B → Agent 1 (Assessor): Visual classification via Gemini Vision
    Step C → Agent 2 (Router): Department routing based on Agent 1 output
    Step D → Compile full ticket document
    Step E → Save to Firestore `tickets` collection
              └─ firebase_service.create_ticket() atomically increments
                 analytics_metadata.datasetVersion (marks cache stale)
    Step F → Enqueue background analytics refresh (non-blocking)
    """
    logger.info(f"📥 New report received at ({latitude}, {longitude})")

    # ------------------------------------------------------------------
    # Step A: Read image bytes and compress to Base64
    # ------------------------------------------------------------------
    try:
        image_bytes = await image.read()
        image_url = image_service.compress_to_base64(image_bytes)
    except Exception as e:
        logger.error(f"❌ Image compression failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image processing failed: {str(e)}"
        )

    # ------------------------------------------------------------------
    # Step B: Agent 1 — The Assessor (Vision AI via Gemini Flash)
    # Sends Base64 string for visual analysis
    # ------------------------------------------------------------------
    try:
        agent1_result = await gemini_service.run_agent1_assessor(
            image_base64_uri=image_url
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
    # Step E: Save to Firestore
    # create_ticket() also calls mark_analytics_stale() internally,
    # so the cache invalidation event is guaranteed even if Step F fails.
    # ------------------------------------------------------------------
    try:
        ticket_id, saved_ticket = firebase_service.create_ticket(ticket_data)
    except Exception as e:
        logger.error(f"❌ Firestore write failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database write failed: {str(e)}"
        )

    # ------------------------------------------------------------------
    # Step F: Enqueue proactive analytics refresh (non-blocking)
    # The background task runs AFTER the 201 response is sent to the client.
    # If Agent 3 fails, the previous cache is preserved and stale=True
    # remains set so the next GET /api/analytics will retry.
    # ------------------------------------------------------------------
    background_tasks.add_task(analytics_service.maybe_regenerate)
    logger.info(f"🔄 Background analytics refresh enqueued for ticket {ticket_id}")

    logger.info(f"🎉 Report pipeline complete. Ticket ID: {ticket_id}")
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success":    True,
            "message":    "Report successfully processed by the AI triage system.",
            "ticket_id":  ticket_id,
            "ticket":     saved_ticket
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
        "count":   len(tickets),
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

    Note: Upvotes do NOT invalidate the analytics cache — they are a community
    engagement signal and do not affect Agent 3's analysis inputs.
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
        "success":          True,
        "ticket_id":        ticket_id,
        "new_upvote_count": new_count
    }


# ---------------------------------------------------------------------------
# GET /api/analytics
# Agent 3 — Predictive Intelligence Dashboard (cache-read only)
# ---------------------------------------------------------------------------

@router.get(
    "/analytics",
    summary="Retrieve cached AI-powered predictive infrastructure analytics",
    description=(
        "Returns the pre-computed analytics cache from Firestore. "
        "Agent 3 (The Analyst) runs asynchronously in the background — "
        "this endpoint NEVER blocks on a Gemini API call. "
        "The `cache_status` field indicates whether the data is fresh or stale. "
        "When stale, a background regeneration is enqueued automatically."
    )
)
async def get_analytics(background_tasks: BackgroundTasks):
    """
    Cache-Read Analytics Endpoint:

    1. Read analytics_cache/latest from Firestore  (~50 ms)
    2. Read analytics_metadata/state to determine staleness (~50 ms)
    3. If stale → enqueue background regeneration (returns immediately)
    4. Return cached data with appropriate cache_status

    Response shape is backward-compatible with the old direct-Gemini endpoint:
      analytics.summary                     ← was: analytics.summary
      analytics.high_risk_clusters          ← was: analytics.high_risk_clusters
      analytics.preventative_recommendations← was: analytics.preventative_recommendations

    New fields added (never break old frontends — they simply ignore unknown keys):
      analytics.heatmapData
      analytics.departmentStatistics
      analytics.categoryStatistics
      analytics.severityDistribution
      analytics.priorityDistribution
      analytics.statusDistribution
      cache_status
      generated_at
    """
    # ---- Step 1: Read metadata (version + stale flag) -----------------
    try:
        metadata = firebase_service.get_analytics_metadata()
    except Exception as e:
        logger.error(f"❌ Failed to read analytics metadata: {e}")
        metadata = None

    dataset_version   = metadata.get("datasetVersion", 0)   if metadata else 0
    analytics_version = metadata.get("analyticsVersion", 0) if metadata else 0
    is_stale          = metadata.get("stale", True)         if metadata else True

    # ---- Step 2: Read the cache document --------------------------------
    try:
        cache = firebase_service.get_analytics_cache()
    except Exception as e:
        logger.error(f"❌ Failed to read analytics cache: {e}")
        cache = None

    # ---- Step 3: Determine cache_status ---------------------------------
    if cache is None and metadata is None:
        # Absolute first boot — no tickets, no cache, no metadata
        cache_status = "building"
    elif cache is None:
        # Metadata exists (tickets have been created) but cache hasn't been
        # written yet — worker is generating for the first time
        cache_status = "building"
    elif is_stale or analytics_version != dataset_version:
        # Cache exists but is outdated — return it immediately, refresh in BG
        cache_status = "stale"
    else:
        cache_status = "fresh"

    # ---- Step 4: Enqueue background regeneration when stale -------------
    if cache_status in ("stale", "building"):
        background_tasks.add_task(analytics_service.maybe_regenerate)
        logger.info(
            f"🔄 Background analytics refresh enqueued "
            f"(cache_status={cache_status}, "
            f"datasetVersion={dataset_version}, "
            f"analyticsVersion={analytics_version})"
        )

    # ---- Step 5: If no cache exists at all — return a graceful response -
    if cache is None:
        logger.info("📭 No analytics cache available yet. Returning empty response.")
        return {
            "success":              True,
            "cache_status":         cache_status,
            "generated_at":         None,
            "ticket_count_analyzed": 0,
            "analytics":            None
        }

    # ---- Step 6: Build the backward-compatible analytics payload --------
    # Map cache field names → original API field names so old frontends
    # continue to work without any changes.
    analytics_payload = {
        # --- Original Agent3Analytics fields (same key names, same structure) ---
        "summary":                     cache.get("executiveSummary", ""),
        "high_risk_clusters":          cache.get("riskClusters", []),
        "preventative_recommendations": cache.get("recommendations", []),

        # --- New enriched fields (additive — old frontends safely ignore them) ---
        "heatmapData":          cache.get("heatmapData", []),
        "departmentStatistics": cache.get("departmentStatistics", {}),
        "categoryStatistics":   cache.get("categoryStatistics", {}),
        "severityDistribution": cache.get("severityDistribution", {}),
        "priorityDistribution": cache.get("priorityDistribution", {}),
        "statusDistribution":   cache.get("statusDistribution", {}),
    }

    logger.info(
        f"⚡ Returning analytics cache "
        f"(status={cache_status}, "
        f"version={cache.get('generatedForVersion')}, "
        f"tickets={cache.get('ticketCount', 0)})"
    )

    return {
        "success":               True,
        "cache_status":          cache_status,
        "generated_at":          cache.get("generatedAt"),
        "ticket_count_analyzed": cache.get("ticketCount", 0),
        "analytics":             analytics_payload
    }


# ---------------------------------------------------------------------------
# POST /api/analytics/regenerate
# Admin endpoint — force-invalidate cache and trigger immediate background refresh
# ---------------------------------------------------------------------------

@router.post(
    "/analytics/regenerate",
    summary="Force-regenerate analytics cache (admin)",
    description=(
        "Immediately invalidates the analytics cache by incrementing datasetVersion "
        "and enqueues a background regeneration. Returns 202 Accepted instantly — "
        "the regeneration runs asynchronously. "
        "Use this after bulk ticket imports or administrative data corrections."
    ),
    status_code=status.HTTP_202_ACCEPTED
)
async def force_regenerate_analytics(background_tasks: BackgroundTasks):
    """
    Admin-triggered cache invalidation + background refresh.

    This endpoint does NOT run Agent 3 synchronously — it returns 202 immediately
    and the regeneration happens in the background, just like the automatic flow.

    To check progress, call GET /api/analytics and inspect the `cache_status` field:
      "building" or "stale" → regeneration is in progress
      "fresh"               → regeneration complete
    """
    logger.info("🔧 Admin: Force-regenerating analytics cache...")

    # Increment datasetVersion to guarantee the worker considers this version new,
    # even if the ticket data hasn't changed since the last run.
    try:
        from datetime import datetime, timezone
        now_iso      = datetime.now(timezone.utc).isoformat()
        current_meta = firebase_service.get_analytics_metadata()
        ticket_count = current_meta.get("ticketCount", 0) if current_meta else 0

        # mark_analytics_stale atomically increments datasetVersion and sets stale=True
        firebase_service.mark_analytics_stale(
            ticket_timestamp=now_iso,
            ticket_count=ticket_count
        )
        logger.info("✅ Cache invalidated. Enqueueing background regeneration...")
    except Exception as e:
        logger.error(f"❌ Failed to invalidate analytics cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache invalidation failed: {str(e)}"
        )

    # Enqueue the background worker — returns to the caller immediately
    background_tasks.add_task(analytics_service.maybe_regenerate)

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "success": True,
            "message": (
                "Analytics cache invalidated. Regeneration started in the background. "
                "Poll GET /api/analytics and check cache_status='fresh' to confirm completion."
            )
        }
    )


import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse

from app.services import firebase_service, gemini_service, image_service

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

    Step A → Compress image and convert to Base64 (Zero-Cost Architecture)
    Step B → Agent 1 (Assessor): Visual classification via Gemini Vision
    Step C → Agent 2 (Router): Department routing based on Agent 1 output
    Step D → Compile full ticket document
    Step E → Save to Firestore `tickets` collection
    """
    logger.info(f"📥 New report received at ({latitude}, {longitude})")

    # ------------------------------------------------------------------
    # Step A: Read image bytes and compress to Base64
    # ------------------------------------------------------------------
    try:
        image_bytes = await image.read()
        
        image_url = image_service.compress_to_base64(image_bytes)
    except Exception as e:
        logger.error(f"❌ Image compression failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image processing failed: {str(e)}"
        )

    # ------------------------------------------------------------------
    # Step B: Agent 1 — The Assessor (Vision AI via Gemini Flash)
    # Sends Base64 string for visual analysis
    # ------------------------------------------------------------------
    try:
        agent1_result = await gemini_service.run_agent1_assessor(
            image_base64_uri=image_url
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
