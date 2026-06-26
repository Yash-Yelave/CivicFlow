# Key Features

CivicFlow offers key functionalities tailored for both citizens and municipal administrators:

## 1. 📍 Hyperlocal Issue Reporting
* **Visual Submission**: Citizens upload image/video evidence of the issue directly from their mobile or desktop browser.
* **Auto-Geolocation**: Automated browser GPS tracking hooks pin the report to an exact geographical coordinate on the map.
* **Context Capture**: Users can add brief descriptive text to supplement visual inputs.

## 2. 🧠 Automated AI Triage (Multi-Agent)
* **Vision Assessor**: Powered by Gemini 1.5 Flash Vision, it scans and parses raw media to classify issues (e.g., "Pothole") and rate severity (High/Medium/Low) without requiring users to navigate complex dropdowns.
* **Smart Workflow Router**: Maps issues to correct municipal bodies (e.g., Road Authority, Electrical Department), sets formal ticket IDs, and priorities.
* **Trend Analyst**: Continuously processes Firestore records to identify hotspot trends and output predictive infrastructure maintenance reports.

## 3. 🗺️ Live Tracking Map
* **Interactive Leaflet Map**: Rendered using OpenStreetMap, displays custom markers for all active issues.
* **Visual Indicators**: Markers are color-coded by department and styled according to severity levels.
* **Detail Card Popups**: Selecting a map marker details the report type, description, photo evidence, current verification count, and target department.

## 4. 👥 Community Verification & Upvoting
* **Validation Mechanics**: Local residents can upvote reported issues to confirm their persistence and severity.
* **Anti-Spam Filter**: Helps prioritize municipal workloads and filter out false reports based on community alignment.

## 5. 📊 Admin & Analytics Insights Dashboard
* **Predictive Trends Panel**: Renders Agent 3's predictions regarding systemic failures (e.g., aging water networks, high hazard zones).
* **Metrics & Analytics**: Summarizes key metrics like open vs. resolved tickets, departmental distribution, and ticket severity breakdowns.
