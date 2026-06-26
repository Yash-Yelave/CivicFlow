"""
CivicFlow Backend — Gemini AI Agent Service
=============================================
Implements the three-agent AI pipeline using Google Gemini 1.5 Flash.

  Agent 1 — The Assessor  : Analyzes uploaded images for infrastructure issues.
  Agent 2 — The Router    : Maps Agent 1 output to municipal departments.
  Agent 3 — The Analyst   : Detects systemic patterns in accumulated ticket data.

All Gemini calls use `response_mime_type="application/json"` to guarantee
valid, parse-ready JSON output — no regex or string-cleaning required.
"""

import os
import json
import logging
from typing import Optional

import google.generativeai as genai
from app.models.schemas import Agent1Assessment, Agent2Routing, Agent3Analytics

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SDK Initialization
# The API key is loaded from environment variables (never hardcoded).
# ---------------------------------------------------------------------------

def _initialize_gemini() -> None:
    """Configure the Gemini SDK with the API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Please add it to your .env file."
        )
    genai.configure(api_key=api_key)
    logger.info("✅ Gemini AI SDK initialized successfully.")


_initialize_gemini()

# Using gemini-1.5-flash for fast, cost-effective multi-modal inference
GEMINI_MODEL = "gemini-1.5-flash"


# ---------------------------------------------------------------------------
# AGENT 1 — The Assessor (Vision AI)
# ---------------------------------------------------------------------------

async def run_agent1_assessor(image_base64_uri: str) -> Agent1Assessment:
    """
    Agent 1: Passes the Base64 image payload to Gemini Vision for infrastructure analysis.

    The agent is instructed to return strict JSON matching the Agent1Assessment schema.
    `response_mime_type="application/json"` ensures Gemini won't wrap output in markdown.

    Args:
        image_base64_uri: The Base64 data URI string (e.g., 'data:image/jpeg;base64,...').

    Returns:
        A validated Agent1Assessment Pydantic model instance.
    """
    logger.info("🤖 Agent 1 (Assessor) starting visual analysis from Base64 string...")

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            # Point Gemini to our exact Pydantic schema structure
            response_schema={
                "type": "object",
                "properties": {
                    "issue_title":    {"type": "string"},
                    "category":       {"type": "string"},
                    "severity_level": {"type": "integer"},
                    "visual_summary": {"type": "string"},
                },
                "required": ["issue_title", "category", "severity_level", "visual_summary"]
            }
        ),
        system_instruction=(
            "You are a senior municipal infrastructure inspector with 20 years of field experience. "
            "Your task is to analyze images of city infrastructure submitted by citizens. "
            "You must identify the exact nature of the issue, classify it accurately, and assign "
            "a severity level from 1 (minor cosmetic issue) to 5 (immediate safety hazard requiring "
            "emergency response). Be precise, factual, and concise. "
            "Always return valid JSON matching the provided schema."
        )
    )

    # Extract mime type and raw base64 data from the URI
    # format: "data:image/jpeg;base64,xxxxxxx"
    header, raw_b64 = image_base64_uri.split(",", 1)
    mime_type = header.split(":")[1].split(";")[0]

    # Build the multi-modal prompt: image data + text instruction
    image_part = {"mime_type": mime_type, "data": raw_b64}
    text_part = (
        "Analyze this image of a city infrastructure issue. "
        "Identify what the problem is, classify it into one of these categories: "
        "[Pothole, Streetlight, Water Leak, Structural Damage, Sewage Overflow, "
        "Road Crack, Fallen Tree, Flooding, Graffiti, Other]. "
        "Assign a severity_level from 1 to 5. "
        "Write a 2-3 sentence visual summary."
    )

    try:
        response = await model.generate_content_async([image_part, text_part])
    except Exception as e:
        logger.error(f"Gemini API error in Agent 1: {e}")
        raise

    # Parse and validate the JSON response against our Pydantic schema
    raw_data = json.loads(response.text)
    assessment = Agent1Assessment(**raw_data)

    logger.info(f"✅ Agent 1 complete: {assessment.issue_title} | Severity: {assessment.severity_level}/5")
    return assessment


# ---------------------------------------------------------------------------
# AGENT 2 — The Router (Municipal Dispatcher)
# ---------------------------------------------------------------------------

async def run_agent2_router(assessment: Agent1Assessment) -> Agent2Routing:
    """
    Agent 2: Receives Agent 1's structured assessment and determines the correct
    municipal routing — department, priority, and recommended action.

    This is a pure text-to-text call; no image is needed at this stage.
    The input is serialized Agent 1 JSON passed as context in the prompt.

    Args:
        assessment: A validated Agent1Assessment Pydantic model from Agent 1.

    Returns:
        A validated Agent2Routing Pydantic model instance.
    """
    logger.info("🤖 Agent 2 (Router) generating municipal ticket...")

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "assigned_department":       {"type": "string"},
                    "ticket_priority":           {"type": "string"},
                    "recommended_action":        {"type": "string"},
                    "estimated_resolution_time": {"type": "string"},
                },
                "required": [
                    "assigned_department", "ticket_priority",
                    "recommended_action", "estimated_resolution_time"
                ]
            }
        ),
        system_instruction=(
            "You are an experienced municipal operations dispatcher in a smart city. "
            "You receive structured infrastructure issue assessments from field inspectors "
            "and must route them to the correct city department. "
            "Available departments: [Public Works Department, Water & Sanitation Department, "
            "Electrical & Streetlight Department, Parks & Recreation Department, "
            "Emergency Services, Urban Planning Department]. "
            "Priority tiers: [CRITICAL (safety hazard, respond now), HIGH (respond in 24hrs), "
            "MEDIUM (respond in 1 week), LOW (scheduled maintenance)]. "
            "Always return valid JSON matching the provided schema."
        )
    )

    # Serialize Agent 1's output as the context for Agent 2
    assessment_json = assessment.model_dump_json(indent=2)
    prompt = (
        f"Based on the following infrastructure issue assessment, determine the correct "
        f"municipal department, assign a priority tier, and specify the recommended action:\n\n"
        f"{assessment_json}\n\n"
        "Return your routing decision strictly as JSON."
    )

    response = model.generate_content(prompt)

    raw_data = json.loads(response.text)
    routing = Agent2Routing(**raw_data)

    logger.info(
        f"✅ Agent 2 complete: → {routing.assigned_department} "
        f"| Priority: {routing.ticket_priority}"
    )
    return routing


# ---------------------------------------------------------------------------
# AGENT 3 — The Analyst (Predictive Intelligence)
# ---------------------------------------------------------------------------

async def run_agent3_analyst(tickets: list[dict]) -> Agent3Analytics:
    """
    Agent 3: Analyzes the full corpus of Firestore tickets to identify
    systemic infrastructure patterns and generate predictive recommendations.

    The agent receives a condensed text summary of all tickets — not raw JSON —
    to keep the token count manageable and the insights human-relevant.

    Args:
        tickets: List of all ticket dictionaries fetched from Firestore.

    Returns:
        A validated Agent3Analytics Pydantic model with clusters and recommendations.
    """
    logger.info(f"🤖 Agent 3 (Analyst) processing {len(tickets)} tickets for pattern detection...")

    if not tickets:
        # Return a safe default if there's no data yet
        return Agent3Analytics(
            summary="No tickets available for analysis yet.",
            high_risk_clusters=[],
            preventative_recommendations=[]
        )

    # -----------------------------------------------------------------------
    # Condense all tickets into a readable summary string for the prompt.
    # This keeps token usage efficient while preserving all key data points.
    # -----------------------------------------------------------------------
    ticket_lines = []
    for i, t in enumerate(tickets, 1):
        a1 = t.get("agent1_assessment", {})
        a2 = t.get("agent2_routing", {})
        lat = t.get("latitude", "N/A")
        lng = t.get("longitude", "N/A")
        ticket_lines.append(
            f"Ticket #{i}: "
            f"Issue='{a1.get('issue_title', 'Unknown')}', "
            f"Category='{a1.get('category', 'Unknown')}', "
            f"Severity={a1.get('severity_level', 0)}/5, "
            f"Department='{a2.get('assigned_department', 'Unknown')}', "
            f"Priority='{a2.get('ticket_priority', 'Unknown')}', "
            f"Status='{t.get('status', 'Pending')}', "
            f"Upvotes={t.get('upvotes', 0)}, "
            f"Location=({lat}, {lng})"
        )
    tickets_summary = "\n".join(ticket_lines)

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "high_risk_clusters": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "sector":       {"type": "string"},
                                "issue_type":   {"type": "string"},
                                "report_count": {"type": "integer"},
                                "risk_level":   {"type": "string"},
                                "insight":      {"type": "string"},
                            }
                        }
                    },
                    "preventative_recommendations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "department": {"type": "string"},
                                "action":     {"type": "string"},
                                "urgency":    {"type": "string"},
                            }
                        }
                    }
                },
                "required": ["summary", "high_risk_clusters", "preventative_recommendations"]
            }
        ),
        system_instruction=(
            "You are a Chief Data Analyst for a smart city municipal operations center. "
            "Your role is to analyze aggregated infrastructure complaint data and identify "
            "systemic issues that indicate deeper problems — not just individual incidents. "
            "Look for geographic clustering (multiple incidents near similar coordinates), "
            "category repetition (many leaks in one area = aging pipe network), and "
            "severity escalation patterns. Generate actionable preventative maintenance "
            "recommendations that can stop small issues from becoming crises. "
            "Be specific, data-driven, and decisive. Always return valid JSON."
        )
    )

    prompt = (
        f"Analyze the following {len(tickets)} active municipal infrastructure tickets "
        f"and identify systemic risk patterns, high-risk geographic clusters, and "
        f"preventative maintenance recommendations:\n\n"
        f"{tickets_summary}\n\n"
        "Focus on: geographic clusters, recurring categories, high-severity trends, "
        "and departments that are overloaded. Return your full analysis as JSON."
    )

    response = model.generate_content(prompt)

    raw_data = json.loads(response.text)
    analytics = Agent3Analytics(**raw_data)

    logger.info(
        f"✅ Agent 3 complete: {len(analytics.high_risk_clusters)} clusters detected, "
        f"{len(analytics.preventative_recommendations)} recommendations generated."
    )
    return analytics
