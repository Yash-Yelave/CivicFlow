# CivicFlow: Autonomous Municipal Triage System

## 1. Project Overview
**Hackathon:** Vibe 2 Ship (codingninjas x Google for Developers)
**Problem Statement Selected:** Problem Statement 2 - Community Hero (Hyperlocal Problem Solver)
**Goal:** To build a platform that enables citizens to identify, report, and track community issues (potholes, leakages, broken streetlights) while utilizing an AI multi-agent system to autonomously categorize, route, and analyze these reports for municipal action.

## 2. Technical Architecture
The system utilizes a 100% free-tier, highly scalable architecture heavily leveraging the Google Cloud and Firebase ecosystems.

### Frontend (Citizen Dashboard)
* **Framework:** React.js (Vite)
* **Mapping:** Leaflet.js + OpenStreetMap (for geolocation and issue mapping)
* **Deployment:** Firebase Hosting (Free Tier)

### Backend (Multi-Agent API)
* **Framework:** FastAPI (Python)
* **Deployment:** Google Cloud Run (Free Tier - scales to zero)
* **AI Engine:** Google AI Studio (Gemini 1.5 Flash API)

### Data & Storage
* **Database:** Firebase Firestore (NoSQL for issue reports, tickets, and verifications)
* **Storage:** Firebase Storage (For user-uploaded images/videos of issues)

## 3. Agentic Workflow (Gemini 1.5 Flash)
The core innovation is the shift from passive reporting to active triage using three distinct AI agents:

1. **Agent 1: The Assessor (Vision AI)**
   * **Trigger:** User uploads a photo/video and location.
   * **Action:** Uses Gemini 1.5 Flash vision capabilities to classify the issue (e.g., "Infrastructure - Pothole"), extract visual severity, and output structured JSON.
2. **Agent 2: The Router (Workflow Automation)**
   * **Trigger:** Receives JSON from The Assessor.
   * **Action:** Determines the correct municipal department (e.g., "Public Works Dept"), drafts a formal maintenance ticket, and assigns a priority level based on location and severity.
3. **Agent 3: The Analyst (Predictive Insights)**
   * **Trigger:** Scheduled API invocation or dashboard request.
   * **Action:** Analyzes clustered Firestore data to generate predictive insights (e.g., "High frequency of water pipe bursts in Sector 4 implies systemic aging infrastructure").

---

## 4. Granular Solo-Developer Phase Breakdown (June 26 - June 29)
Since you are executing this project single-handedly, the timeline is tightly optimized into logical, chronological blocks to avoid context-switching bottlenecks.

### Phase 1: Environment, Database Setup & AI Core (June 26 - Target: End of Day)
* [ ] **Task 1.1: Firebase Project Provisioning**
  * Create a new project in the Firebase Console.
  * Enable **Firestore Database** in production mode and configure initial security rules allowing authenticated/public reads/writes for testing.
  * Enable **Firebase Storage** and set up an `issue_images/` bucket.
  * Download the Firebase Admin SDK private key JSON file for backend configuration.
* [ ] **Task 1.2: Backend Architecture Initialization**
  * Bootstrap a boilerplate FastAPI repository with a virtual environment (`venv`).
  * Install dependencies: `fastapi`, `uvicorn`, `firebase-admin`, `google-generativeai`, `pydantic`, `python-multipart`.
  * Create `main.py` and set up cross-origin resource sharing (CORS) middleware to accept requests from the local React frontend.
* [ ] **Task 1.3: Gemini Multi-Agent System Prompting**
  * Initialize the `google-generativeai` SDK using an API key from Google AI Studio.
  * Define Pydantic response models to enforce strict, predictable schema structures for Agent 1 and Agent 2 outputs.
  * Write precise system instructions for **Agent 1 (The Assessor)** to accept images and output a JSON categorization with structural integrity.
  * Write system instructions for **Agent 2 (The Router)** to receive that JSON data and map it to specific municipal departments.

### Phase 2: Backend Integration & API Pipeline (June 27 - Target: Morning to Afternoon)
* [ ] **Task 2.1: File Upload & Storage Routing**
  * Build an endpoint `/api/report` in FastAPI that accepts multipart form data (image file, latitude, longitude, user description).
  * Implement logic to write the uploaded file directly into Firebase Storage and retrieve its public access URL.
* [ ] **Task 2.2: Chaining Agent 1 & Agent 2**
  * Construct the execution logic within the `/api/report` endpoint:
    1. Pass the public image URL (or raw bytes) to Agent 1 to classify the anomaly.
    2. Pipe Agent 1's structured JSON output straight into Agent 2.
    3. Merge the geolocation, user description, image URL, and Agent 2's departmental ticket details into a uniform document format.
* [ ] **Task 2.3: Firestore Data Persistence**
  * Write the final unified document into a Firestore collection named `tickets`.
  * Verify data structures using the Firebase local emulator or direct database console checking.
* [ ] **Task 2.4: Agent 3 (The Analyst) Implementation**
  * Build a separate endpoint `/api/analytics` that fetches all current entries from the Firestore `tickets` collection.
  * Package the entries into a text summary block and feed it to Gemini 1.5 Flash with system instructions to return localized trend predictions and high-priority hotspots.

### Phase 3: Frontend Development & Mapping Dashboard (June 27 - Target: Evening)
* [ ] **Task 3.1: Frontend Scaffolding**
  * Scaffold a new React application using Vite: `npm create vite@latest frontend -- --template react`.
  * Install UI libraries and dependencies: `leaflet`, `react-leaflet`, `lucide-react`, `axios`.
* [ ] **Task 3.2: Map Component Integration**
  * Configure Leaflet maps inside the app layout using OpenStreetMap tiles.
  * Write geolocation capture hooks to pull the user's browser location accurately upon opening the application.
* [ ] **Task 3.3: Reporting Interface Construction**
  * Build a minimalist reporting overlay panel: includes a file selector for captured images, text field for optional description, and a submission loading state handler.
  * Wire the submit event handler to send a standard `POST` request containing FormData to your local FastAPI endpoint.

### Phase 4: Community Features & Frontend Wiring (June 28 - Target: Morning)
* [ ] **Task 4.1: Live Map Tracking Elements**
  * Build a wrapper component that pulls existing active tickets from Firestore (via FastAPI or direct SDK) and populates them as custom markers on the OpenStreetMap interface.
  * Style marker popups to show the classification, severity badge, and AI-assigned department.
* [ ] **Task 4.2: Community Verification Architecture**
  * Create upvote buttons inside map popups allowing other local citizens to validate active issues.
  * Build a simple patch request endpoint in FastAPI (`/api/tickets/{id}/verify`) to increment the verification counter within Firestore.
* [ ] **Task 4.3: Analytical Dashboard View**
  * Design a secondary view tab within the layout dedicated to administrative/community insights.
  * Connect this view to your `/api/analytics` endpoint, cleanly rendering Agent 3's predictions in an elegant, minimal text-card dashboard.

### Phase 5: Containerization & Google Cloud Deployment (June 28 - Target: Afternoon to Night)
* [ ] **Task 5.1: Backend Dockerization**
  * Write a standard `Dockerfile` for your FastAPI backend pinning Python 3.10+, copying code files, installing dependencies, and exposing port 8080.
  * Build and test the Docker container image locally to ensure error-free start-up behaviors.
* [ ] **Task 5.2: Google Cloud Run Implementation**
  * Set up the Google Cloud SDK CLI on your development environment.
  * Submit your backend image to Google Artifact Registry or build it directly via Cloud Build.
  * Deploy the service to **Google Cloud Run** using the command line or the Google Cloud Console.
  * Ensure the parameter `--allow-unauthenticated` is explicitly passed so that the API handles frontend traffic seamlessly without access token validation walls.
* [ ] **Task 5.3: Frontend Deployment to Firebase Hosting**
  * Create an production build of the React client: `npm run build`.
  * Execute `firebase login` and running `firebase init hosting` inside the project folder root.
  * Point the public hosting path to the `dist/` build target folder.
  * Execute `firebase deploy --only hosting` to acquire your active frontend deployment web address.

### Phase 6: Final Testing, Refinement & Hackathon Submission (June 29 - Target: Before 2:00 PM)
* [ ] **Task 6.1: End-to-End System Verification**
  * Perform a cold-start diagnostic verification on the fully deployed frontend and backend web links.
  * Test the exact rate limitations (ensuring concurrent clicks don't hit Google AI Studio's 15 RPM barrier).
* [ ] **Task 6.2: Open-Source Repository Document Polish**
  * Push clean code files to a public GitHub repository. Ensure secrets (`.env` keys, service account JSON configuration parameters) are strictly contained in `.gitignore` and omitted from tracking history.
  * Fill the repository `README.md` containing links, structural drawings, configurations, and a quick-start manual.
* [ ] **Task 6.3: Submission Execution via BlockseBlock**
  * Construct a shared public Google Doc holding your comprehensive feature set, architecture schema layout, and Google technical components list as required by the submission guidelines.
  * Head to your personal dashboard space on BlockseBlock before the hard 2:00 PM deadline, enter your unique project identifier name, and submit all mandatory fields.

---

## 5. Evaluation Matrix Alignment Tracker
* **Agentic Depth (20%):** Validated by explicit hand-offs and pipeline chaining across Assessor, Router, and Analyst models.
* **Innovation & Creativity (20%):** Validated through automated vision classifications removing legacy dropdown selection mechanics from municipal complaint paradigms.
* **Usage of Google Technologies (15%):** Fully covered via comprehensive implementations of Firebase Storage, Firestore, Hosting, Cloud Run, and Google AI Studio APIs.
* **Product Experience & Design (10%):** Fulfilled by clean Leaflet map integrations, active data widgets, and real-time community upvoting features.
