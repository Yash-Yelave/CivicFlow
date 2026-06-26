# Google Technologies Utilized

CivicFlow leverages Google and Firebase free-tier infrastructure, ensuring cost-efficiency, seamless scaling, and developer productivity.

## 1. 🧠 Google AI Studio & Gemini 1.5 Flash
The core logic relies on **Gemini 1.5 Flash** due to its low latency, high throughput, and robust multimodal capabilities:
* **Assessor Agent**: Harnesses Gemini's vision capability to analyze image uploads, identify anomalies, and output a structured JSON categorization.
* **Router Agent**: Consumes Assessor’s classification JSON data to automate department assignment and draft municipal tickets.
* **Analyst Agent**: Processes bulk reports using Gemini's large context window to extract predictive insights and hotspot trends.

## 2. 🗄️ Firebase Firestore (NoSQL Database)
* **Real-time Synchronization**: Acts as the single source of truth for all active tickets, coordinates, department routing, and verification metrics.
* **Scalable Data Retrieval**: Feeds real-time map marker positions and admin analysis datasets instantly.

## 3. 📂 Firebase Storage
* **Media Assets**: Serves as the storage bucket for user-uploaded photographs or video recordings.
* **Public URL Retrieval**: Generates secure links that the FastAPI pipeline passes to Gemini for multimodal vision inspection.

## 4. 🌐 Firebase Hosting
* **Static Assets Hosting**: Deploys the production React-Vite frontend bundle. It is integrated with global CDNs to ensure fast delivery.

## 5. 🐳 Google Cloud Run
* **Containerized Serverless Execution**: Hosts the FastAPI Docker container backend. Scales down to zero active instances when no requests are being processed, eliminating runtime idle costs.
