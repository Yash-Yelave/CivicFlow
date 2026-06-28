# Changelog

All notable changes to the **CivicFlow** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] - Planning Phase
### Added
- Setup and scaffolding for upcoming Flutter mobile application environment.
- Implementation plan for GIS Heatmaps and predictive ML maintenance scoring.

---

## [v1.1.0] - Analytics Cache Refactor
### Changed
- **Analytics Cache Refactor**: Completely redesigned Agent 3 (The Analyst) from a synchronous, per-request execution model to a high-performance **Event-Driven Cached Architecture**.
- Dashboard reads now return instantly (<50ms) by fetching from the `analytics_cache/latest` Firestore document.

### Added
- **Background Analytics Worker**: Generates analytics asynchronously via FastAPI `BackgroundTasks`.
- **Event-Driven Invalidation**: Ticket creations and mutations automatically increment the `datasetVersion` and mark the analytics metadata as stale.
- **Manual Refresh Endpoint**: Added `POST /api/analytics/regenerate` to allow administrative force-refreshing of the analytics cache.
- Pure Python calculations for heatmap generation, department statistics, and category statistics to reduce Gemini token usage.
- Optimistic locking in Firestore to prevent duplicate concurrent background generation tasks.

### Improved
- **Performance**: Dashboard latency reduced from ~5-10s to <50ms.
- **Scalability**: Token consumption massively reduced as LLM inference only runs when underlying data has structurally changed.

---

## [v1.0.0] - Initial Release (Hackathon MVP)
### Added
#### Frontend
- React.js (Vite) Single Page Application.
- Leaflet.js and OpenStreetMap integration for geolocation and issue mapping.
- Reporting interface with base64 image compression.
- Live community verification and upvoting system.

#### Backend
- FastAPI backend architecture running on Python.
- Firebase Admin SDK integration for Firestore persistence and Storage handling.
- Zero-cost multipart form handling converting images to compressed Base64 strings.

#### AI & Multi-Agent Pipeline
- Google AI Studio (Gemini 2.5 Flash) integration.
- **Agent 1 (The Assessor)**: Vision AI classification of uploaded issue images.
- **Agent 2 (The Router)**: Workflow automation for mapping Assessor outputs to municipal departments.
- **Agent 3 (The Analyst - Legacy)**: Synchronous predictive insights generation based on aggregate reports.

#### Deployment
- Docker containerization for the backend.
- Preparation for Google Cloud Run (Backend) and Firebase Hosting (Frontend) deployments.
