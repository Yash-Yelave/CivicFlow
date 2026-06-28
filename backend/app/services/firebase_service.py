"""
CivicFlow Backend — Firebase Service
=======================================
Handles all Firebase interactions (Firestore ONLY).
Image storage via Firebase Storage has been removed in favor of Base64 strings.

This module is imported as a singleton dependency by the API routes.
"""

import os
import logging
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Singleton: Initialize Firebase Admin SDK exactly once at module load.
# The credential file path is read from environment vars.
# ---------------------------------------------------------------------------

def _initialize_firebase() -> None:
    """
    Bootstraps the Firebase Admin SDK.
    Safe to call multiple times — skips re-initialization if already done.
    """
    if firebase_admin._apps:
        # Already initialized
        return

    service_account_path = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_KEY",
        "app/core/serviceAccountKey.json"  # Default path relative to backend/
    )

    if not os.path.exists(service_account_path):
        raise FileNotFoundError(
            f"Firebase credentials not found at: '{service_account_path}'. "
            "Please set FIREBASE_SERVICE_ACCOUNT_KEY in your .env file."
        )

    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
    logger.info("✅ Firebase Admin SDK (Firestore ONLY) initialized successfully.")


# Run initialization when this module is first imported
_initialize_firebase()

# Module-level reference to Firestore client
db = firestore.client()

# ---------------------------------------------------------------------------
# Collection / document constants — single source of truth for all paths
# ---------------------------------------------------------------------------
TICKETS_COLLECTION       = "tickets"
ANALYTICS_CACHE_COLL     = "analytics_cache"
ANALYTICS_CACHE_DOC      = "latest"          # analytics_cache/latest
ANALYTICS_METADATA_COLL  = "analytics_metadata"
ANALYTICS_METADATA_DOC   = "state"           # analytics_metadata/state


# ===========================================================================
# TICKETS — CRUD
# ===========================================================================

# ---------------------------------------------------------------------------
# Firestore — Create Ticket
# ---------------------------------------------------------------------------

def create_ticket(ticket_data: dict) -> tuple[str, dict]:
    """
    Saves a compiled triage ticket document to the Firestore 'tickets' collection.

    After a successful write, the analytics metadata is automatically marked stale
    so the background worker knows to regenerate the cache on the next request.

    Args:
        ticket_data: A dictionary containing all ticket fields (including Base64 image).

    Returns:
        A tuple of (document_id, ticket_data_with_id).
    """
    # Add a server-side ISO timestamp before writing
    now_iso = datetime.now(timezone.utc).isoformat()
    ticket_data["created_at"] = now_iso

    # Use Firestore's auto-generated document ID
    doc_ref = db.collection(TICKETS_COLLECTION).document()
    doc_ref.set(ticket_data)

    ticket_id = doc_ref.id
    ticket_data["ticket_id"] = ticket_id

    logger.info(f"🗂️  Ticket saved to Firestore with ID: {ticket_id}")

    # -----------------------------------------------------------------------
    # Analytics cache invalidation event — TICKET CREATED
    # Incrementing datasetVersion signals the worker to regenerate the cache.
    # This is a fire-and-forget Firestore write; it never blocks the response.
    # -----------------------------------------------------------------------
    try:
        _ticket_count = len(get_all_tickets())  # lightweight count for metadata
        mark_analytics_stale(ticket_timestamp=now_iso, ticket_count=_ticket_count)
    except Exception as e:
        # A stale-marking failure must NEVER propagate to the caller.
        # The ticket is already saved; analytics staleness is non-critical.
        logger.warning(f"⚠️  Failed to mark analytics stale after ticket create: {e}")

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

    Upvotes are community signals and do NOT affect analytics-relevant data
    (category, severity, department, status), so no cache invalidation is triggered.

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


# ---------------------------------------------------------------------------
# Firestore — Update Arbitrary Ticket Fields
# ---------------------------------------------------------------------------

def update_ticket_fields(ticket_id: str, fields: dict) -> dict:
    """
    Updates one or more fields on a specific ticket document and marks the
    analytics cache stale when analytics-relevant fields change.

    Analytics-relevant fields (trigger cache invalidation):
        status, severity_level, category, assigned_department

    Args:
        ticket_id: The Firestore document ID of the ticket to update.
        fields:    A dictionary of field names and their new values.

    Returns:
        The updated ticket document as a dict.

    Raises:
        ValueError: If the ticket does not exist.
    """
    ANALYTICS_RELEVANT_FIELDS = {"status", "severity_level", "category", "assigned_department"}

    doc_ref = db.collection(TICKETS_COLLECTION).document(ticket_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise ValueError(f"Ticket '{ticket_id}' not found in Firestore.")

    now_iso = datetime.now(timezone.utc).isoformat()
    fields["updated_at"] = now_iso
    doc_ref.update(fields)

    updated_doc = doc_ref.get().to_dict()
    updated_doc["ticket_id"] = ticket_id

    logger.info(f"✏️  Ticket '{ticket_id}' updated: {list(fields.keys())}")

    # Invalidate analytics cache only when data that Agent 3 cares about changes
    if ANALYTICS_RELEVANT_FIELDS.intersection(fields.keys()):
        try:
            ticket_count = len(get_all_tickets())
            mark_analytics_stale(ticket_timestamp=now_iso, ticket_count=ticket_count)
        except Exception as e:
            logger.warning(f"⚠️  Failed to mark analytics stale after ticket update: {e}")

    return updated_doc


# ===========================================================================
# ANALYTICS METADATA — analytics_metadata/state
# Tracks datasetVersion, analyticsVersion, stale flag, and optimistic lock.
# ===========================================================================

def get_analytics_metadata() -> dict | None:
    """
    Reads the current analytics state document from `analytics_metadata/state`.

    Returns:
        The metadata dict if the document exists, otherwise None.
        On first boot (before any ticket is created), this will return None.
    """
    doc = (
        db.collection(ANALYTICS_METADATA_COLL)
          .document(ANALYTICS_METADATA_DOC)
          .get()
    )
    if doc.exists:
        return doc.to_dict()
    logger.info("📋 analytics_metadata/state does not exist yet (first boot).")
    return None


def mark_analytics_stale(ticket_timestamp: str, ticket_count: int) -> None:
    """
    Atomically increments `datasetVersion` and sets `stale=True`.

    Called whenever a ticket is created or an analytics-relevant field changes.
    This is the single write-path for all cache invalidation events.

    Uses a Firestore transaction to guarantee the increment is atomic even
    if multiple requests fire simultaneously (e.g., batch imports).

    Args:
        ticket_timestamp: ISO-8601 timestamp of the triggering ticket event.
        ticket_count:     Current total number of tickets (for metadata bookkeeping).
    """
    meta_ref = (
        db.collection(ANALYTICS_METADATA_COLL)
          .document(ANALYTICS_METADATA_DOC)
    )

    @firestore.transactional
    def _run_in_transaction(transaction):
        snapshot = meta_ref.get(transaction=transaction)
        if snapshot.exists:
            existing = snapshot.to_dict()
            current_version = existing.get("datasetVersion", 0)
        else:
            # First-time initialization — create the metadata document
            existing = {}
            current_version = 0

        new_version = current_version + 1
        transaction.set(meta_ref, {
            "datasetVersion":        new_version,
            # analyticsVersion stays unchanged — the worker will update it
            "analyticsVersion":      existing.get("analyticsVersion", 0),
            "stale":                 True,
            "latestTicketTimestamp": ticket_timestamp,
            "ticketCount":           ticket_count,
            # Preserve fields the worker may have written
            "lastAnalyticsRun":      existing.get("lastAnalyticsRun"),
            "generationInProgress":  existing.get("generationInProgress", False),
        }, merge=False)

        logger.info(
            f"🔔 Analytics stale flag set. "
            f"datasetVersion: {current_version} → {new_version}"
        )

    transaction = db.transaction()
    _run_in_transaction(transaction)


def update_analytics_version(new_version: int, run_timestamp: str) -> None:
    """
    Called by the analytics worker after a successful cache generation.

    Sets analyticsVersion = new_version, clears stale=False,
    clears generationInProgress=False, and records lastAnalyticsRun.

    Args:
        new_version:   The datasetVersion the worker just processed.
        run_timestamp: ISO-8601 timestamp of when generation completed.
    """
    meta_ref = (
        db.collection(ANALYTICS_METADATA_COLL)
          .document(ANALYTICS_METADATA_DOC)
    )
    meta_ref.update({
        "analyticsVersion":     new_version,
        "stale":                False,
        "generationInProgress": False,
        "lastAnalyticsRun":     run_timestamp,
    })
    logger.info(f"✅ Analytics metadata updated. analyticsVersion={new_version}, stale=False")


def set_generation_in_progress(in_progress: bool) -> None:
    """
    Sets the optimistic-lock flag on the metadata document.

    True  → a worker has claimed this generation run; others must skip.
    False → the run is complete (or failed); the next request may trigger one.

    Args:
        in_progress: Whether generation is currently running.
    """
    meta_ref = (
        db.collection(ANALYTICS_METADATA_COLL)
          .document(ANALYTICS_METADATA_DOC)
    )
    # Use merge=True so this write never overwrites other fields
    meta_ref.set({"generationInProgress": in_progress}, merge=True)
    logger.debug(f"🔒 generationInProgress → {in_progress}")


# ===========================================================================
# ANALYTICS CACHE — analytics_cache/latest
# Stores the full serialized Agent 3 output for fast dashboard reads.
# ===========================================================================

def get_analytics_cache() -> dict | None:
    """
    Reads the cached analytics document from `analytics_cache/latest`.

    Returns:
        The cache dict if the document exists, otherwise None.
    """
    doc = (
        db.collection(ANALYTICS_CACHE_COLL)
          .document(ANALYTICS_CACHE_DOC)
          .get()
    )
    if doc.exists:
        logger.info("⚡ Analytics cache hit — returning stored results.")
        return doc.to_dict()
    logger.info("📭 Analytics cache miss — no cached document found.")
    return None


def write_analytics_cache(cache_data: dict) -> None:
    """
    Writes (overwrites) the analytics cache document at `analytics_cache/latest`.

    The document is fully replaced on each write — no partial merges —
    so the cache is always in a consistent, fully-populated state.

    Args:
        cache_data: A dictionary matching the AnalyticsCache schema.
    """
    (
        db.collection(ANALYTICS_CACHE_COLL)
          .document(ANALYTICS_CACHE_DOC)
          .set(cache_data)          # set() replaces the entire document
    )
    logger.info(
        f"💾 Analytics cache written. "
        f"generatedForVersion={cache_data.get('generatedForVersion')}"
    )
