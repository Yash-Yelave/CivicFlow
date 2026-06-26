# Solution Overview

CivicFlow transforms citizen reporting from a passive, slow-moving administrative queue into an active, automated, and intelligent response pipeline.

## 🛠️ The Core Mechanism

1. **Hyperlocal Identification**: Using a mobile-friendly web dashboard, citizens upload photos/videos of community issues, and the system automatically captures their high-precision GPS coordinates.
2. **Autonomous Multi-Agent Triage**: Instead of relying on manual ticket classification and routing by municipal employees, CivicFlow deploys three specialized AI agents powered by **Gemini 1.5 Flash**:
   * **Agent 1: The Assessor (Vision AI)**: Analyzes user-submitted media to determine the category (e.g., road damage, utility leak, electrical hazard) and severity of the issue, outputting a structured JSON schema.
   * **Agent 2: The Router (Workflow Automation)**: Consumes the JSON output from Agent 1, determines the responsible department (e.g., Public Works, Water Sanitation, Power Grid), assigns a priority score, and constructs a detailed ticket.
   * **Agent 3: The Analyst (Predictive Insights)**: Clustered analysis on Firestore tickets to identify broader community issues (such as recurring plumbing leaks indicating aging water mains in a sector).
3. **Community Validation**: Localized upvoting allows citizens to endorse and verify reports, reducing spam and helping municipal authorities prioritize high-impact issues.
4. **Interactive Tracking Map**: A real-time Leaflet.js-based map displaying reported issues, color-coded by severity, department, and resolution status.
