"""
CivicFlow Backend — Firebase Service
=======================================
Handles all Firebase interactions:
  - Admin SDK initialization (Firestore + Storage)
  - Image upload to Firebase Storage
  - Firestore CRUD operations for the 'tickets' collection

This module is imported as a singleton dependency by the API routes.
"""

import os
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1 import FieldFilter

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Singleton: Initialize Firebase Admin SDK exactly once at module load.
# The credential file path and storage bucket are read from environment vars.
# ---------------------------------------------------------------------------

def _initialize_firebase() -> None:
    """
    Bootstraps the Firebase Admin SDK.
    Safe to call multiple times — skips re-initialization if already done.
    """
    if firebase_admin._apps:
        # Already initialized (e.g., hot-reload in dev mode)
        return

    service_account_path = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_KEY",
        "app/core/serviceAccountKey.json"  # Default path relative to backend/
    )
    storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")

    if not os.path.exists(service_account_path):
        raise FileNotFoundError(
            f"Firebase credentials not found at: '{service_account_path}'. "
            "Please set FIREBASE_SERVICE_ACCOUNT_KEY in your .env file."
        )

    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred, {
        "storageBucket": storage_bucket
    })
    logger.info("✅ Firebase Admin SDK initialized successfully.")


# Run initialization when this module is first imported
_initialize_firebase()

# Module-level references to Firestore and Storage clients
db = firestore.client()
bucket = storage.bucket()

# The Firestore collection where all triage tickets are stored
TICKETS_COLLECTION = "tickets"


# ---------------------------------------------------------------------------
# Firebase Storage — Image Upload
# ---------------------------------------------------------------------------

async def upload_image_to_storage(
    image_bytes: bytes,
    original_filename: str,
    content_type: str
) -> str:
    """
    Uploads an image to Firebase Storage and returns a public download URL.

    Args:
        image_bytes: Raw bytes of the uploaded image file.
        original_filename: Original filename from the upload (used for extension).
        content_type: MIME type (e.g., 'image/jpeg').

    Returns:
        A publicly accessible URL string for the uploaded image.
    """
    # Generate a unique filename to avoid collisions in the storage bucket
    file_extension = original_filename.rsplit(".", 1)[-1] if "." in original_filename else "jpg"
    unique_filename = f"issue_images/{uuid.uuid4()}.{file_extension}"

    # Create a blob reference in the Firebase Storage bucket
    blob = bucket.blob(unique_filename)

    # Upload the raw bytes
    blob.upload_from_string(image_bytes, content_type=content_type)

    # Make the file publicly readable so the frontend and Gemini can access it
    blob.make_public()

    public_url = blob.public_url
    logger.info(f"📸 Image uploaded to Firebase Storage: {public_url}")
    return public_url


# ---------------------------------------------------------------------------
# Firestore — Create Ticket
# ---------------------------------------------------------------------------

def create_ticket(ticket_data: dict) -> tuple[str, dict]:
    """
    Saves a compiled triage ticket document to the Firestore 'tickets' collection.

    Args:
        ticket_data: A dictionary containing all ticket fields (location, agents, etc.)

    Returns:
        A tuple of (document_id, ticket_data_with_id).
    """
    # Add a server-side ISO timestamp before writing
    ticket_data["created_at"] = datetime.now(timezone.utc).isoformat()

    # Use Firestore's auto-generated document ID
    doc_ref = db.collection(TICKETS_COLLECTION).document()
    doc_ref.set(ticket_data)

    ticket_id = doc_ref.id
    ticket_data["ticket_id"] = ticket_id

    logger.info(f"🗂️  Ticket saved to Firestore with ID: {ticket_id}")
    return ticket_id, ticket_data


# ---------------------------------------------------------------------------
# Firestore — Get All Tickets
# ---------------------------------------------------------------------------

def get_all_tickets() -> list[dict]:
    """
    Retrieves all documents from the 'tickets' Firestore collection.

    Returns:
        A list of ticket dictionaries, each including their document ID.
    """
    docs = db.collection(TICKETS_COLLECTION).stream()
    tickets = []
    for doc in docs:
        ticket = doc.to_dict()
        ticket["ticket_id"] = doc.id  # Inject the Firestore document ID
        tickets.append(ticket)

    logger.info(f"📋 Fetched {len(tickets)} tickets from Firestore.")
    return tickets


# ---------------------------------------------------------------------------
# Firestore — Upvote / Verify Ticket
# ---------------------------------------------------------------------------

def increment_ticket_upvotes(ticket_id: str) -> int:
    """
    Atomically increments the 'upvotes' field on a specific ticket document.
    Uses Firestore's server-side Increment to prevent race conditions.

    Args:
        ticket_id: The Firestore document ID of the ticket to upvote.

    Returns:
        The new upvote count after incrementing.

    Raises:
        ValueError: If the ticket_id does not correspond to an existing document.
    """
    doc_ref = db.collection(TICKETS_COLLECTION).document(ticket_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise ValueError(f"Ticket '{ticket_id}' not found in Firestore.")

    # Atomic server-side increment — safe for concurrent requests
    doc_ref.update({"upvotes": firestore.Increment(1)})

    # Fetch updated document to return the new count
    updated_doc = doc_ref.get()
    new_count = updated_doc.to_dict().get("upvotes", 1)

    logger.info(f"👍 Ticket '{ticket_id}' upvoted. New count: {new_count}")
    return new_count
