"""
CivicFlow Backend — Analytics Service
=======================================
Implements the event-driven analytics cache worker.

Architecture overview:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Ticket mutation (create / update)                                      │
  │       │                                                                 │
  │       ▼                                                                 │
  │  firebase_service.mark_analytics_stale()                                │
  │       │  atomically increments datasetVersion, sets stale=True          │
  │       ▼                                                                 │
  │  GET /api/analytics  ──► reads analytics_cache/latest  ──► returns fast │
  │       │  (if stale) enqueues AnalyticsService.maybe_regenerate()        │
  │       │                                                                 │
  │       ▼  (BackgroundTask — non-blocking)                                │
  │  AnalyticsService.maybe_regenerate()                                    │
  │       │  reads metadata, checks versions, claims optimistic lock        │
  │       ▼                                                                 │
  │  AnalyticsService._regenerate()                                         │
  │       │  1. load all tickets                                            │
  │       │  2. compute derived stats (Python — zero Gemini cost)           │
  │       │  3. invoke run_agent3_analyst() exactly once                    │
  │       │  4. validate AnalyticsCache schema                              │
  │       │  5. write analytics_cache/latest                                │
  │       │  6. update analyticsVersion, stale=False                        │
  │       │                                                                 │
  │  On failure: release lock, keep old cache, leave stale=True             │
  └─────────────────────────────────────────────────────────────────────────┘

Key guarantees:
  • The dashboard endpoint NEVER blocks on Gemini.
  • Gemini Agent 3 is invoked at most ONCE per datasetVersion increment.
  • Two concurrent requests cannot both trigger a regeneration run.
  • Cache failure leaves the previous result intact.
"""

import logging
from collections import Counter
from datetime import datetime, timezone

from app.services import firebase_service
from app.services.gemini_service import run_agent3_analyst

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Singleton-pattern service that manages the analytics cache lifecycle.

    Usage (from a FastAPI BackgroundTask):
        analytics_service = AnalyticsService()
        background_tasks.add_task(analytics_service.maybe_regenerate)
    """

    # ------------------------------------------------------------------
    # Public entry point — called by BackgroundTasks
    # ------------------------------------------------------------------

    async def maybe_regenerate(self) -> None:
        """
        Checks whether the analytics cache needs regenerating and, if so,
        claims the optimistic lock and runs the full generation pipeline.

        This method is always called asynchronously (non-blocking from the
        perspective of the user-facing request). It is safe to call on every
        GET /api/analytics request — it will skip quickly if not needed.

        Decision logic:
          1. Read analytics_metadata/state from Firestore.
          2. If metadata is missing → first boot, treat as stale.
          3. If stale=False and analyticsVersion == datasetVersion → cache is
             fresh; exit immediately (the common fast-path).
          4. If generationInProgress=True → another worker already claimed
             this run; exit to avoid duplicate work.
          5. Otherwise → claim the lock and start _regenerate().
        """
        logger.info("🔍 AnalyticsService: Checking if regeneration is needed...")

        # ---- Step 1: Read metadata ----------------------------------------
        metadata = firebase_service.get_analytics_metadata()

        if metadata is None:
            logger.info("ℹ️  No analytics metadata found. Checking if there are existing tickets...")
            tickets = firebase_service.get_all_tickets()
            ticket_count = len(tickets)
            if ticket_count > 0:
                logger.info(f"📊 Found {ticket_count} existing tickets on first boot. Initializing metadata...")
                now_iso = datetime.now(timezone.utc).isoformat()
                firebase_service.mark_analytics_stale(ticket_timestamp=now_iso, ticket_count=ticket_count)
                metadata = firebase_service.get_analytics_metadata()
            else:
                logger.info("ℹ️  No tickets found. Writing empty analytics cache.")
                self._write_empty_cache(dataset_version=0, generation_start=datetime.now(timezone.utc))
                self._finalize(dataset_version=0, generation_start=datetime.now(timezone.utc))
                return

        dataset_version   = metadata.get("datasetVersion", 0)
        analytics_version = metadata.get("analyticsVersion", 0)
        is_stale          = metadata.get("stale", True)
        already_running   = metadata.get("generationInProgress", False)

        # ---- Step 2: Fast-path exit — cache is fresh ----------------------
        if not is_stale and analytics_version == dataset_version:
            logger.info(
                f"✅ Analytics cache is fresh (v{analytics_version}). "
                "Skipping regeneration."
            )
            return

        # ---- Step 3: Optimistic lock — another worker is running ----------
        if already_running:
            logger.info(
                "🔒 Another analytics worker is already running "
                "(generationInProgress=True). Skipping duplicate run."
            )
            return

        # ---- Step 4: Claim the lock and run --------------------------------
        logger.info(
            f"🚀 Analytics cache is stale "
            f"(datasetVersion={dataset_version}, analyticsVersion={analytics_version}). "
            "Claiming lock and starting regeneration..."
        )

        try:
            firebase_service.set_generation_in_progress(True)
            await self._regenerate(dataset_version=dataset_version)
        except Exception as e:
            # ------------------------------------------------------------------
            # Error recovery:
            # • Release the lock so the next request can retry.
            # • Leave stale=True so the system knows the cache is outdated.
            # • The previous cache document is untouched — the dashboard
            #   continues to serve old (but valid) data until next success.
            # ------------------------------------------------------------------
            logger.error(
                f"❌ Analytics regeneration failed: {e}",
                exc_info=True
            )
            try:
                firebase_service.set_generation_in_progress(False)
            except Exception as lock_err:
                logger.error(
                    f"❌ Failed to release generationInProgress lock: {lock_err}"
                )

    # ------------------------------------------------------------------
    # Core generation pipeline — private
    # ------------------------------------------------------------------

    async def _regenerate(self, dataset_version: int) -> None:
        """
        Full analytics generation pipeline. Called only after the optimistic
        lock has been claimed by maybe_regenerate().

        Steps:
          1. Load all tickets from Firestore.
          2. Compute deterministic derived statistics (Python — no LLM cost).
          3. Invoke Gemini Agent 3 exactly once.
          4. Build and validate the AnalyticsCache document.
          5. Write to analytics_cache/latest.
          6. Update analyticsVersion and clear stale + lock flags.

        Args:
            dataset_version: The datasetVersion we are regenerating for.
                             Used to detect a version race (another ticket
                             arrived while we were generating).
        """
        generation_start = datetime.now(timezone.utc)

        # ---- Step 1: Load all tickets -----------------------------------
        logger.info("📥 Loading all tickets for analytics generation...")
        tickets = firebase_service.get_all_tickets()
        ticket_count = len(tickets)
        logger.info(f"📊 Loaded {ticket_count} tickets.")

        # If the DB is empty, write a safe default and exit cleanly
        if ticket_count == 0:
            logger.info("ℹ️  No tickets found. Writing empty analytics cache.")
            self._write_empty_cache(dataset_version, generation_start)
            self._finalize(dataset_version, generation_start)
            return

        # ---- Step 2: Compute deterministic derived statistics -----------
        logger.info("📐 Computing derived statistics (no Gemini call)...")
        derived = self._compute_derived_stats(tickets)

        # ---- Step 3: Invoke Gemini Agent 3 ------------------------------
        logger.info("🤖 Invoking Gemini Agent 3 (The Analyst)...")
        analytics_result = await run_agent3_analyst(tickets)
        logger.info(
            f"✅ Agent 3 complete: "
            f"{len(analytics_result.high_risk_clusters)} clusters, "
            f"{len(analytics_result.preventative_recommendations)} recommendations."
        )

        # ---- Step 4: Build the full cache document ----------------------
        generated_at = datetime.now(timezone.utc).isoformat()

        cache_doc = {
            # Provenance
            "generatedAt":          generated_at,
            "generatedForVersion":  dataset_version,
            "ticketCount":          ticket_count,

            # Agent 3 output — field names match AnalyticsCache schema
            # and are backward-compatible with the old Agent3Analytics shape:
            #   executiveSummary  ↔  analytics.summary (old field name preserved in response)
            #   riskClusters      ↔  analytics.high_risk_clusters
            #   recommendations   ↔  analytics.preventative_recommendations
            "executiveSummary":     analytics_result.summary,
            "riskClusters":         [rc.model_dump() for rc in analytics_result.high_risk_clusters],
            "recommendations":      [pr.model_dump() for pr in analytics_result.preventative_recommendations],

            # Deterministic derived stats (computed in Python — zero extra Gemini cost)
            "heatmapData":          derived["heatmap_data"],
            "departmentStatistics": derived["department_statistics"],
            "categoryStatistics":   derived["category_statistics"],
            "severityDistribution": derived["severity_distribution"],
            "priorityDistribution": derived["priority_distribution"],
            "statusDistribution":   derived["status_distribution"],
        }

        # ---- Step 5: Persist to Firestore --------------------------------
        logger.info("💾 Writing analytics cache to Firestore...")
        firebase_service.write_analytics_cache(cache_doc)

        # ---- Step 6: Update metadata and release lock --------------------
        self._finalize(dataset_version, generation_start)

        logger.info(
            f"🎉 Analytics regeneration complete in "
            f"{(datetime.now(timezone.utc) - generation_start).total_seconds():.2f}s. "
            f"Covers {ticket_count} tickets at version v{dataset_version}."
        )

    # ------------------------------------------------------------------
    # Derived statistics — pure Python, zero Gemini cost
    # ------------------------------------------------------------------

    def _compute_derived_stats(self, tickets: list[dict]) -> dict:
        """
        Computes all statistics that can be derived deterministically from
        the ticket data without calling Gemini.

        These computations are O(n) in the number of tickets and run in-process
        in milliseconds, making them far cheaper than an LLM call.

        Returns a dict with:
          heatmap_data          — [{lat, lng, weight}] for every ticket
          department_statistics — {department_name: count}
          category_statistics   — {category_name: count}
          severity_distribution — {1: count, 2: count, ..., 5: count}
          priority_distribution — {CRITICAL: count, HIGH: count, ...}
          status_distribution   — {Pending: count, Resolved: count, ...}
        """
        heatmap_data = []
        departments  = []
        categories   = []
        severities   = []
        priorities   = []
        statuses     = []

        for ticket in tickets:
            a1 = ticket.get("agent1_assessment", {})
            a2 = ticket.get("agent2_routing", {})

            # ------ Heatmap point ----------------------------------------
            lat = ticket.get("latitude")
            lng = ticket.get("longitude")
            sev = a1.get("severity_level", 1)

            if lat is not None and lng is not None:
                # Normalize weight: severity 1→0.2, severity 5→1.0
                weight = round(sev / 5.0, 2)
                heatmap_data.append({"lat": lat, "lng": lng, "weight": weight})

            # ------ Categorical counters ---------------------------------
            dept = a2.get("assigned_department", "Unknown")
            cat  = a1.get("category", "Unknown")
            pri  = a2.get("ticket_priority", "Unknown")
            sta  = ticket.get("status", "Pending")

            departments.append(dept)
            categories.append(cat)
            priorities.append(pri)
            statuses.append(sta)

            # Severity as a string key so Firestore accepts it as a map key
            severities.append(str(sev) if sev else "Unknown")

        return {
            "heatmap_data":          heatmap_data,
            "department_statistics": dict(Counter(departments)),
            "category_statistics":   dict(Counter(categories)),
            "severity_distribution": dict(Counter(severities)),
            "priority_distribution": dict(Counter(priorities)),
            "status_distribution":   dict(Counter(statuses)),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _write_empty_cache(self, dataset_version: int, generation_start: datetime) -> None:
        """
        Writes a safe, empty analytics cache document.
        Called when there are no tickets in the database yet.
        """
        generated_at = generation_start.isoformat()
        firebase_service.write_analytics_cache({
            "generatedAt":          generated_at,
            "generatedForVersion":  dataset_version,
            "ticketCount":          0,
            "executiveSummary":     "No tickets have been submitted yet.",
            "riskClusters":         [],
            "recommendations":      [],
            "heatmapData":          [],
            "departmentStatistics": {},
            "categoryStatistics":   {},
            "severityDistribution": {},
            "priorityDistribution": {},
            "statusDistribution":   {},
        })

    def _finalize(self, dataset_version: int, generation_start: datetime) -> None:
        """
        Updates analytics metadata after a successful generation run.
        Sets analyticsVersion = dataset_version, stale=False, and
        clears the generationInProgress lock.

        Args:
            dataset_version:   The version just processed.
            generation_start:  When generation began (used for lastAnalyticsRun).
        """
        run_timestamp = generation_start.isoformat()
        firebase_service.update_analytics_version(
            new_version=dataset_version,
            run_timestamp=run_timestamp
        )
        # Lock is also cleared inside update_analytics_version — this is the
        # single authoritative path; no need for a separate set_generation_in_progress call.


# ---------------------------------------------------------------------------
# Module-level singleton instance
# Imported by routes.py so every request shares the same object.
# ---------------------------------------------------------------------------

analytics_service = AnalyticsService()
