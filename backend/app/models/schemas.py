"""
CivicFlow Backend — Pydantic Models
=====================================
Strict schema definitions for AI agent responses and API payloads.
Using Pydantic v2 for data validation across the entire pipeline.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


# ---------------------------------------------------------------------------
# AGENT 1 — The Assessor (Vision AI)
# Schema enforced on Gemini's JSON response after visual analysis.
# ---------------------------------------------------------------------------

class Agent1Assessment(BaseModel):
    """
    Structured output from Agent 1 (The Assessor).
    Gemini returns this after analyzing the uploaded infrastructure image.
    """
    issue_title: str = Field(
        description="A concise, human-readable title for the detected infrastructure issue.",
        example="Severe Pothole on Main Arterial Road"
    )
    category: str = Field(
        description="The type of infrastructure issue detected.",
        example="Pothole"
        # Possible values: Pothole, Streetlight, Water Leak, Structural Damage,
        # Sewage Overflow, Road Crack, Fallen Tree, Graffiti, Other
    )
    severity_level: int = Field(
        ge=1, le=5,
        description="Severity score from 1 (cosmetic) to 5 (critical/safety hazard)."
    )
    visual_summary: str = Field(
        description="A brief 1-2 sentence summary of what the AI visually observed in the image."
    )


# ---------------------------------------------------------------------------
# AGENT 2 — The Router (Workflow / Municipal Dispatcher)
# Schema enforced on Gemini's JSON after receiving Agent 1's assessment.
# ---------------------------------------------------------------------------

class Agent2Routing(BaseModel):
    """
    Structured output from Agent 2 (The Router).
    Gemini determines the correct department and action based on Agent 1's data.
    """
    assigned_department: str = Field(
        description="The municipal department responsible for resolving this issue.",
        example="Public Works Department"
        # Possible values: Public Works Department, Water & Sanitation Dept,
        # Electrical & Streetlight Dept, Parks & Recreation Dept,
        # Emergency Services, Urban Planning Dept
    )
    ticket_priority: str = Field(
        description="Priority tier based on severity and category.",
        example="HIGH"
        # Possible values: CRITICAL, HIGH, MEDIUM, LOW
    )
    recommended_action: str = Field(
        description="The specific action the assigned department should take."
    )
    estimated_resolution_time: str = Field(
        description="Estimated time to resolve (e.g., '24-48 hours', '1 week')."
    )


# ---------------------------------------------------------------------------
# AGENT 3 — The Analyst (Predictive Intelligence)
# Schema enforced on Gemini's response for the analytics dashboard.
# ---------------------------------------------------------------------------

class RiskCluster(BaseModel):
    """A single high-risk cluster identified by Agent 3."""
    sector: str = Field(description="Geographic area or sector name.")
    issue_type: str = Field(description="The type of issue forming a cluster.")
    report_count: int = Field(description="Number of reports contributing to this cluster.")
    risk_level: str = Field(description="Risk assessment: CRITICAL, HIGH, or MEDIUM.")
    insight: str = Field(description="Agent 3's human-readable insight about this cluster.")


class PreventativeRecommendation(BaseModel):
    """A single preventative action recommended by Agent 3."""
    department: str = Field(description="Target municipal department.")
    action: str = Field(description="Specific preventative maintenance action.")
    urgency: str = Field(description="How urgently this should be actioned.")


class Agent3Analytics(BaseModel):
    """
    Full structured output from Agent 3 (The Analyst).
    Drives the 'Predictive Insights' dashboard view on the frontend.
    This is what Gemini writes — it is persisted into analytics_cache/latest.
    """
    summary: str = Field(description="High-level executive summary of the city's infrastructure health.")
    high_risk_clusters: List[RiskCluster] = Field(
        description="List of detected geographic clusters with recurring or critical issues."
    )
    preventative_recommendations: List[PreventativeRecommendation] = Field(
        description="Concrete preventative actions to prevent escalation."
    )


# ---------------------------------------------------------------------------
# ANALYTICS CACHE — Firestore persistence layer (analytics_cache/latest)
# Stores the full analytics result plus derived statistics computed in Python.
# ---------------------------------------------------------------------------

class HeatmapPoint(BaseModel):
    """A single weighted point for the risk heatmap layer on the frontend map."""
    lat: float = Field(description="Latitude of the ticket.")
    lng: float = Field(description="Longitude of the ticket.")
    weight: float = Field(description="Normalized risk weight (severity / 5).")


class AnalyticsCache(BaseModel):
    """
    Mirrors the `analytics_cache/latest` Firestore document.

    Contains the complete Agent 3 output merged with deterministic statistics
    derived from the raw ticket data (no Gemini required for these fields).
    All new fields are Optional so the system degrades gracefully if an older
    cache document exists in Firestore without the new fields.
    """
    # Provenance / versioning
    generatedAt: str = Field(description="ISO-8601 timestamp when this cache was written.")
    generatedForVersion: int = Field(
        description="The datasetVersion this cache corresponds to."
    )

    # Agent 3 outputs (mapped from Agent3Analytics)
    executiveSummary: str = Field(
        description="High-level executive summary — same as Agent3Analytics.summary."
    )
    riskClusters: List[dict] = Field(
        default_factory=list,
        description="Serialised RiskCluster list from Agent 3."
    )
    recommendations: List[dict] = Field(
        default_factory=list,
        description="Serialised PreventativeRecommendation list from Agent 3."
    )

    # Deterministic derived statistics (computed in Python, no LLM cost)
    heatmapData: Optional[List[dict]] = Field(
        default=None,
        description="[{lat, lng, weight}] for every ticket — drives the map heatmap layer."
    )
    departmentStatistics: Optional[dict] = Field(
        default=None,
        description="Ticket count keyed by assigned_department."
    )
    categoryStatistics: Optional[dict] = Field(
        default=None,
        description="Ticket count keyed by issue category."
    )


# ---------------------------------------------------------------------------
# ANALYTICS METADATA — Firestore state document (analytics_metadata/state)
# Tracks versioning and staleness for the cache invalidation system.
# ---------------------------------------------------------------------------

class AnalyticsMetadata(BaseModel):
    """
    Mirrors the `analytics_metadata/state` Firestore document.

    datasetVersion    — incremented every time a ticket event changes analytics-relevant data.
    analyticsVersion  — set equal to datasetVersion after a successful cache write.
    stale             — True when datasetVersion > analyticsVersion.
    generationInProgress — optimistic lock flag to prevent concurrent regeneration.
    """
    datasetVersion: int = Field(default=0, description="Monotonically increasing ticket mutation counter.")
    analyticsVersion: int = Field(default=0, description="Version for which the cache was last generated.")
    stale: bool = Field(default=True, description="True when cached analytics are outdated.")
    lastAnalyticsRun: Optional[str] = Field(default=None, description="ISO timestamp of last successful run.")
    latestTicketTimestamp: Optional[str] = Field(default=None, description="ISO timestamp of most-recently mutated ticket.")
    ticketCount: int = Field(default=0, description="Number of tickets at the time of last metadata update.")
    generationInProgress: bool = Field(
        default=False,
        description="Optimistic lock: True while a background worker is actively generating analytics."
    )


# ---------------------------------------------------------------------------
# API RESPONSE — GET /api/analytics
# The public envelope returned to the frontend.
# The `analytics` dict is backward-compatible with the old Agent3Analytics shape.
# ---------------------------------------------------------------------------

class AnalyticsResponse(BaseModel):
    """
    Full API response for GET /api/analytics.

    cache_status values:
      "fresh"    — cache is up-to-date (datasetVersion == analyticsVersion)
      "stale"    — returned old cache; background worker has been triggered
      "building" — no cache exists yet; worker is running for the first time
      "error"    — cache is unavailable (worker failed and no prior cache exists)
    """
    success: bool
    cache_status: str = Field(description="fresh | stale | building | error")
    generated_at: Optional[str] = Field(default=None, description="When the cache was last generated.")
    ticket_count_analyzed: int = Field(default=0)
    analytics: Optional[dict] = Field(
        default=None,
        description="Full analytics payload — includes all Agent 3 fields plus derived statistics."
    )


# ---------------------------------------------------------------------------
# API RESPONSE — Full Ticket Document stored in Firestore
# ---------------------------------------------------------------------------

class TicketResponse(BaseModel):
    """
    Represents a compiled triage ticket as it appears in Firestore
    and is returned to the frontend after a successful report submission.
    """
    ticket_id: str
    image_url: str
    latitude: float
    longitude: float
    description: Optional[str] = None
    status: str = "Pending"
    upvotes: int = 1
    agent1_assessment: dict
    agent2_routing: dict
    created_at: str
