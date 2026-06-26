"""
CivicFlow Frontend — API Service Layer (api.js)
================================================
Centralized Axios client for all CivicFlow backend API calls.

All functions are async and return the `data` payload directly.
Each function includes try/catch so calling components can manage
their own loading/error UI states cleanly.

Usage in a React component:
  import { getTickets, submitReport, verifyTicket, getAnalytics } from '../services/api';
*/

import axios from 'axios';

// ---------------------------------------------------------------------------
// Base Configuration
// Reads the backend URL from the Vite environment variable.
// For local dev: create a .env.local file with VITE_API_URL=http://localhost:8080
// For production: set VITE_API_URL to your Cloud Run service URL.
// ---------------------------------------------------------------------------

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Axios instance with shared base URL and sensible timeout defaults
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60s timeout — Gemini multi-agent calls can take time
  headers: {
    'Accept': 'application/json',
    // Note: Do NOT set 'Content-Type' here globally.
    // multipart/form-data requires Axios to set the boundary automatically.
  },
});

// ---------------------------------------------------------------------------
// Request / Response Interceptors (optional but useful for debugging)
// ---------------------------------------------------------------------------

apiClient.interceptors.request.use(
  (config) => {
    console.log(`📡 [CivicFlow API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unknown API error occurred.';
    console.error(`❌ [CivicFlow API Error] ${message}`);
    return Promise.reject(new Error(message));
  }
);


// ===========================================================================
// API FUNCTIONS
// ===========================================================================


// ---------------------------------------------------------------------------
// 1. POST /api/report
//    Submit a new infrastructure issue through the multi-agent AI pipeline.
//
//    The backend expects multipart/form-data with:
//      - image      (File)
//      - latitude   (float, as string in FormData)
//      - longitude  (float, as string in FormData)
//      - description (string, optional)
//
//    Example usage in React:
//      const result = await submitReport({
//        imageFile: fileInputRef.current.files[0],
//        latitude: position.lat,
//        longitude: position.lng,
//        description: "Large pothole near the intersection"
//      });
//      console.log(result.ticket_id); // Firestore document ID
// ---------------------------------------------------------------------------

export const submitReport = async ({ imageFile, latitude, longitude, description = '' }) => {
  // Build FormData — the correct way to send files + text fields together
  const formData = new FormData();
  formData.append('image', imageFile);                     // File object from <input type="file">
  formData.append('latitude', String(latitude));           // Must be stringified for FormData
  formData.append('longitude', String(longitude));
  if (description) {
    formData.append('description', description);
  }

  try {
    const response = await apiClient.post('/api/report', formData, {
      headers: {
        // Axios will automatically set the correct multipart/form-data boundary
        // when we do NOT override Content-Type here. This is critical.
        'Content-Type': 'multipart/form-data',
      },
      // Track upload progress for a loading indicator (optional)
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / (progressEvent.total || 1)
        );
        console.log(`📤 Upload progress: ${percentCompleted}%`);
      },
    });
    return response.data; // { success, message, ticket_id, ticket }
  } catch (error) {
    throw error; // Re-throw so the calling component can handle UI feedback
  }
};


// ---------------------------------------------------------------------------
// 2. GET /api/tickets
//    Fetch all active triage tickets for the Leaflet map feed.
//
//    Example usage in React (inside useEffect):
//      const { tickets } = await getTickets();
//      // tickets is an array of { ticket_id, latitude, longitude, agent1_assessment, ... }
// ---------------------------------------------------------------------------

export const getTickets = async () => {
  try {
    const response = await apiClient.get('/api/tickets');
    return response.data; // { success, count, tickets: [...] }
  } catch (error) {
    throw error;
  }
};


// ---------------------------------------------------------------------------
// 3. PATCH /api/tickets/{ticketId}/verify
//    Community upvote — increments the upvote count on a specific ticket.
//
//    Example usage in React:
//      const result = await verifyTicket('abc123firestore_id');
//      setUpvoteCount(result.new_upvote_count);
// ---------------------------------------------------------------------------

export const verifyTicket = async (ticketId) => {
  try {
    const response = await apiClient.patch(`/api/tickets/${ticketId}/verify`);
    return response.data; // { success, ticket_id, new_upvote_count }
  } catch (error) {
    throw error;
  }
};


// ---------------------------------------------------------------------------
// 4. GET /api/analytics
//    Trigger Agent 3 (The Analyst) for predictive infrastructure insights.
//
//    Example usage in React (inside AnalyticsDashboard):
//      const { analytics } = await getAnalytics();
//      // analytics.high_risk_clusters → array of { sector, issue_type, ... }
//      // analytics.preventative_recommendations → array of { department, action, ... }
// ---------------------------------------------------------------------------

export const getAnalytics = async () => {
  try {
    const response = await apiClient.get('/api/analytics');
    return response.data; // { success, ticket_count_analyzed, analytics: { ... } }
  } catch (error) {
    throw error;
  }
};

export default apiClient;
