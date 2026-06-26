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
    """
    summary: str = Field(description="High-level executive summary of the city's infrastructure health.")
    high_risk_clusters: List[RiskCluster] = Field(
        description="List of detected geographic clusters with recurring or critical issues."
    )
    preventative_recommendations: List[PreventativeRecommendation] = Field(
        description="Concrete preventative actions to prevent escalation."
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
