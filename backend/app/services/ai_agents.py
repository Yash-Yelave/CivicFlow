"""
CivicFlow — Core AI Logic Module
=================================
Initializes the Google Generative AI SDK and defines the multi-agent pipeline 
using strict Pydantic schemas for guaranteed structured output.

Agents:
  - Agent 1 (Assessor): Analyzes uploaded images for infrastructure issues.
  - Agent 2 (Router): Determines department routing and priority based on Agent 1 data.
"""

import os
import json
import logging
from typing import Literal

from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel, ValidationError

# Initialize logger for this module
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SDK Initialization
# ---------------------------------------------------------------------------

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv()

def _init_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)

_init_gemini()

# Define the models to be used
GEMINI_MODEL = "gemini-1.5-flash"


# ---------------------------------------------------------------------------
# Pydantic Schemas (The Contracts)
# ---------------------------------------------------------------------------

class AssessorResult(BaseModel):
    issue_title: str
    category: Literal["Pothole", "Streetlight", "Leak", "Vandalism", "Waste", "Other"]
    severity_level: int  # 1-5
    visual_evidence_summary: str

class RouterResult(BaseModel):
    assigned_department: str
    recommended_action: str
    priority_status: Literal["Low", "Medium", "High", "Critical"]


# ---------------------------------------------------------------------------
# Agent 1: The Assessor (Vision Model)
# ---------------------------------------------------------------------------

async def run_assessor_agent(base64_image: str) -> dict:
    """
    Agent 1: Analyzes the provided Base64 image and extracts structured data about the issue.
    
    Args:
        base64_image: A Base64 data URI (e.g., 'data:image/jpeg;base64,...').
        
    Returns:
        A dictionary representation of the AssessorResult schema.
        
    Raises:
        ValueError: If the image URI is malformed or the Gemini response is invalid/unparseable.
    """
    logger.info("🤖 Agent 1 (Assessor) beginning image analysis...")
    
    try:
        # Extract mime type and raw base64 data from the URI
        if "," not in base64_image:
            raise ValueError("Malformed Base64 image string. Expected format: 'data:image/jpeg;base64,...'")
        
        header, raw_b64 = base64_image.split(",", 1)
        mime_type = header.split(":")[1].split(";")[0]
        
        image_part = {"mime_type": mime_type, "data": raw_b64}
        
    except Exception as e:
        logger.error(f"Failed to parse Base64 image payload: {e}")
        raise ValueError(f"Failed to parse Base64 image payload: {str(e)}")

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=(
            "You are an expert municipal infrastructure inspector. Analyze the provided image of a city issue. "
            "Categorize the issue, determine its severity (1 being cosmetic, 5 being a severe public hazard), "
            "and summarize the visual evidence. You must output raw JSON."
        ),
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=AssessorResult.model_json_schema()
        )
    )

    try:
        # Prompt Gemini with the image and a brief instruction
        prompt = "Analyze this image and return the structured assessment JSON."
        response = await model.generate_content_async([image_part, prompt])
        
        # Parse and validate the response
        raw_data = json.loads(response.text)
        validated_data = AssessorResult(**raw_data)
        
        logger.info(f"✅ Agent 1 complete: {validated_data.issue_title} ({validated_data.category})")
        return validated_data.model_dump()
        
    except ValidationError as ve:
        logger.error(f"Agent 1 output failed schema validation: {ve}")
        raise ValueError("Agent 1 returned malformed or unexpected data structure.")
    except Exception as e:
        logger.error(f"Agent 1 API call failed: {e}")
        raise RuntimeError(f"Agent 1 failed during execution: {str(e)}")


# ---------------------------------------------------------------------------
# Agent 2: The Router (Text Model)
# ---------------------------------------------------------------------------

async def run_router_agent(assessor_data: dict) -> dict:
    """
    Agent 2: Determines routing and priority based on Agent 1's assessment.
    
    Args:
        assessor_data: The dictionary output from Agent 1 (AssessorResult).
        
    Returns:
        A dictionary representation of the RouterResult schema.
        
    Raises:
        ValueError: If the Gemini response is invalid or fails schema validation.
    """
    logger.info("🤖 Agent 2 (Router) determining department routing...")
    
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=(
            "You are an autonomous municipal dispatcher. Review the infrastructure assessment data provided. "
            "Assign the issue to the correct city department (e.g., Public Works, Water Management, Traffic Control), "
            "define a priority status based on the severity, and provide a 1-sentence recommended action plan. "
            "You must output raw JSON."
        ),
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=RouterResult.model_json_schema()
        )
    )
    
    try:
        # Format the Assessor data as a string prompt
        prompt = f"Assessment Data: {json.dumps(assessor_data)}"
        response = await model.generate_content_async(prompt)
        
        # Parse and validate the response
        raw_data = json.loads(response.text)
        validated_data = RouterResult(**raw_data)
        
        logger.info(f"✅ Agent 2 complete: Routed to {validated_data.assigned_department} ({validated_data.priority_status})")
        return validated_data.model_dump()
        
    except ValidationError as ve:
        logger.error(f"Agent 2 output failed schema validation: {ve}")
        raise ValueError("Agent 2 returned malformed or unexpected data structure.")
    except Exception as e:
        logger.error(f"Agent 2 API call failed: {e}")
        raise RuntimeError(f"Agent 2 failed during execution: {str(e)}")
