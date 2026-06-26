# CivicFlow Architecture

This document describes the design, components, and data flow of the CivicFlow system.

## 🧱 Component Diagrams

```mermaid
graph TD
    subgraph Client ["Citizen Frontend (React + Leaflet)"]
        UI[Upload Panel / Live Map]
        Map[Interactive OpenStreetMap]
    end

    subgraph API ["Multi-Agent Backend (FastAPI / Docker)"]
        Server[FastAPI Router]
        Agent1[Agent 1: Assessor]
        Agent2[Agent 2: Router]
        Agent3[Agent 3: Analyst]
    end

    subgraph Firebase ["Firebase Ecosystem"]
        Firestore[(Firestore Database)]
        Storage[(Firebase Storage)]
    end

    subgraph LLM ["Google AI Studio"]
        Gemini[Gemini 1.5 Flash API]
    end

    UI -->|1. Upload Image & Geolocation| Server
    Server -->|2. Store Media| Storage
    Storage -->|3. Media URL| Server
    Server -->|4. Request Image Analysis| Agent1
    Agent1 -->|5. Vision Prompt & Image| Gemini
    Gemini -->|6. JSON Assessment| Agent1
    Agent1 -->|7. Pipeline JSON Output| Agent2
    Agent2 -->|8. Request Departmental Routing| Gemini
    Gemini -->|9. JSON Ticket Details| Agent2
    Agent2 -->|10. Formatted Ticket Document| Server
    Server -->|11. Write Ticket Data| Firestore
    Map -->|12. Real-time Markers Sync| Firestore

    UI -->|13. Request Analytics| Server
    Server -->|14. Fetch All Tickets| Firestore
    Server -->|15. Request Trend Prediction| Agent3
    Agent3 -->|16. Prompt with Data| Gemini
    Gemini -->|17. Markdown Predictions| Agent3
    Agent3 -->|18. Return Insights| UI
```

---

## 🚦 End-to-End Data Flow

### 1. Issue Reporting Pipeline
1. **Reporting Input**: A citizen opens the web application, which requests browser-level GPS permissions to capture geographical coordinates (Latitude & Longitude).
2. **Media Capture**: The user captures or selects an image/video of the issue, adds an optional text description, and hits the "Submit" button.
3. **Multipart Form POST**: The client submits a multipart form request containing coordinates, text description, and raw image bytes to `/api/report`.
4. **Cloud Object Upload**: The FastAPI server receives the upload and transfers the image to **Firebase Storage** (under `issue_images/`). It retrieves the public URL for the newly stored image.
5. **Agent 1 (The Assessor)**: The backend prompts Gemini 1.5 Flash using the image URL and specific assessment system instructions. Gemini returns a validated JSON string outlining classification and severity.
6. **Agent 2 (The Router)**: The backend routes Agent 1's JSON evaluation into Agent 2. Gemini maps the evaluation to a specific municipal department (e.g., Water and Sewerage Board), constructs a ticket title, and flags standard tags.
7. **Persistence**: The FastAPI backend merges the user description, coordinates, image URL, and Agent 2's departmental ticket details, storing it as a unified document in the **Firebase Firestore** collection `tickets`.
8. **Real-time Map Sync**: The citizen map dashboard automatically syncs with the `tickets` collection, rendering the new issue marker instantly.

### 2. Analytics Generation Pipeline
1. **Analytics View Request**: An administrator or user clicks on the "Analytics" tab, firing a `GET` request to `/api/analytics`.
2. **Firestore Read**: FastAPI reads all existing documents in the `tickets` collection.
3. **Agent 3 (The Analyst)**: The backend aggregates the raw ticket list (category, coordinates, department, date) and feeds it to Gemini 1.5 Flash. The agent processes the clusters to predict infrastructure failures (e.g., aging sewer pipelines in a specific zone) and returns structured markdown insights.
4. **Display**: The insights are served to the frontend and rendered in a clean cards component.
