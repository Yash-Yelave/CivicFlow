# Technologies Used

CivicFlow leverages a modern, highly scalable, and cost-effective tech stack.

## Frontend (Citizen & Admin Portal)
* **React.js & Vite**: Modern React framework scaffolded with Vite for fast HMR (Hot Module Replacement) and optimized production builds.
* **Leaflet.js & React-Leaflet**: Lightweight, mobile-friendly interactive mapping library using OpenStreetMap tiles.
* **Axios**: Promised-based HTTP client for API communication with the FastAPI backend.
* **Lucide React**: Crisp, modern icon package for UI elements.
* **CSS3 (Vanilla CSS)**: Structured styling utilizing custom CSS variables for premium look & feel, transitions, and layout alignment.

## Backend (Multi-Agent System)
* **FastAPI (Python)**: High-performance, modern Web framework for building APIs with Python 3.10+ based on standard Python type hints.
* **Uvicorn**: Asynchronous Server Gateway Interface (ASGI) web server implementation for Python.
* **Pydantic**: Data validation and settings management using Python type annotations. Utilized to enforce schema integrity on Gemini JSON outputs.
* **Python-Multipart**: Form data parser for handling multipart/form-data requests (image/file uploads).

## AI Engine
* **Google Generative AI SDK**: Integrates Python applications with the Gemini API to construct the multi-agent orchestration pipeline.

## Hosting & Database (Google Cloud / Firebase Ecosystem)
* **Firebase Firestore**: Scalable NoSQL cloud database for storing and syncing data in real-time.
* **Firebase Storage**: Object storage for hosting user-submitted images and videos.
* **Firebase Hosting**: Fast and secure hosting for React static assets.
* **Google Cloud Run**: Serverless container hosting platform for scaling the FastAPI backend service to zero when idle.
* **Docker**: Containerization utility to ensure parity between local development and Cloud Run staging environments.
