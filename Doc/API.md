# CivicFlow API Reference

This document outlines the REST API endpoints provided by the FastAPI backend for the CivicFlow application.

---

## POST `/api/report`

**Purpose**: Submit a new community issue. Triggers the Agent 1 (Assessor) and Agent 2 (Router) pipeline to automatically classify, route, and store the ticket in Firestore. This also enqueues a background task to invalidate and regenerate the analytics cache.

- **Method**: POST
- **Headers**: `Content-Type: multipart/form-data`
- **Authentication**: None required (MVP phase).

### Request Parameters (FormData)
| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | The image or photo of the issue. |
| `latitude` | Float | Yes | GPS latitude of the issue. |
| `longitude`| Float | Yes | GPS longitude of the issue. |
| `description`| String | No | Optional context provided by the citizen. |

### Response Schema
```json
{
  "success": true,
  "message": "Report analyzed and routed successfully",
  "ticket": {
    "ticket_id": "auto-generated-uuid",
    "timestamp": "2026-06-28T09:00:00Z",
    "image_url": "base64-string-or-url",
    "location": {"lat": 18.5, "lng": 73.8},
    "description": "...",
    "upvotes": 0,
    "status": "Open",
    "ai_assessment": {
      "category": "Infrastructure",
      "severity": "High",
      "summary": "Large pothole in center lane"
    },
    "routing": {
      "department": "Public Works",
      "priority": "P1",
      "recommended_action": "Dispatch road crew within 24h"
    }
  }
}
```
**Performance Notes**: Processing time depends heavily on Gemini 2.5 Flash image analysis latency (typically 2-4 seconds).

---

## GET `/api/tickets`

**Purpose**: Fetch all active community tickets to render on the map dashboard.

- **Method**: GET
- **Headers**: None
- **Authentication**: None required.

### Response Schema
```json
{
  "success": true,
  "tickets": [
    {
      "id": "uuid",
      "timestamp": "...",
      "location": {"lat": 18.5, "lng": 73.8},
      "ai_assessment": {"category": "Infrastructure", "severity": "High"},
      "upvotes": 5
      // ... full ticket schema
    }
  ]
}
```

---

## PATCH `/api/tickets/{id}/verify`

**Purpose**: Allows community members to upvote/verify an existing ticket, incrementing its verification count in Firestore.

- **Method**: PATCH
- **URL Parameter**: `id` (String) - The Firestore document ID of the ticket.

### Response Schema
```json
{
  "success": true,
  "message": "Verification added",
  "new_upvote_count": 6
}
```

---

## GET `/api/analytics`

**Purpose**: Retrieve predictive analytics, risk clusters, and recommendations. Used by the Analytics Dashboard.

- **Method**: GET
- **Architecture**: Reads directly from the `analytics_cache/latest` Firestore document.

### Response Schema
```json
{
  "success": true,
  "cache_status": "fresh",
  "generated_at": "2026-06-28T09:00:00Z",
  "ticket_count_analyzed": 142,
  "analytics": {
    "summary": "Overall city infrastructure status is...",
    "high_risk_clusters": [
      {
        "cluster_name": "Downtown Potholes",
        "description": "High concentration of road damage",
        "risk_level": "High"
      }
    ],
    "preventative_recommendations": [
      {
        "department": "Public Works",
        "action": "Pre-emptive resurfacing of Main St."
      }
    ],
    "heatmapData": [{"lat": 18.5, "lng": 73.8, "weight": 5}],
    "departmentStatistics": {"Public Works": 50, "Sanitation": 20},
    "categoryStatistics": {"Infrastructure": 45}
  }
}
```
**Performance Notes**: Returns in <50ms. No LLM execution occurs on this request. If the cache is currently being built for the first time, `cache_status` will be `"building"`.

---

## POST `/api/analytics/regenerate`

**Purpose**: Administrative endpoint to forcefully invalidate the analytics cache and trigger a background regeneration.

- **Method**: POST
- **Headers**: None (can be secured via Admin token in the future).

### Response Schema
```json
{
  "success": true,
  "message": "Analytics regeneration queued in background.",
  "status": "building"
}
```
**Performance Notes**: Returns HTTP 202 Accepted immediately. The actual Gemini generation occurs asynchronously.
