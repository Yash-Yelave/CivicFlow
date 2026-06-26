import React from 'react';
import { MapContainer, TileLayer, Marker, ZoomControl } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { renderToStaticMarkup } from 'react-dom/server';

// Map severity_level (1–5) to a marker color
const severityToColor = (level) => {
  if (level >= 5) return '#ef4444'; // Red — Critical
  if (level >= 4) return '#f97316'; // Orange — Severe
  if (level >= 3) return '#f59e0b'; // Amber — Pending
  return '#22c55e';                 // Green — Low
};

/**
 * Creates a custom circular Leaflet div icon with a severity-based color ring.
 * Renders a React SVG to an HTML string for maximum cross-browser compatibility.
 */
const createIssueMarker = (severityLevel = 3) => {
  const color = severityToColor(severityLevel);
  const html = renderToStaticMarkup(
    <div style={{
      width: 32, height: 32,
      background: 'white',
      borderRadius: '50%',
      border: `3px solid ${color}`,
      boxShadow: `0 0 0 3px ${color}22, 0 4px 12px rgba(0,0,0,0.15)`,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      cursor: 'pointer',
    }}>
      <div style={{
        width: 10, height: 10,
        background: color,
        borderRadius: '50%',
      }} />
    </div>
  );

  return L.divIcon({
    html,
    className: '',          // Remove Leaflet's default ugly white box
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -20],
  });
};

const MapFeed = ({ issues = [], onMarkerClick, userPosition }) => {
  // Center on user GPS if available, else default to New Delhi
  const center = userPosition
    ? [userPosition.lat, userPosition.lng]
    : [28.6139, 77.2090];

  return (
    <div className="w-full h-full rounded-3xl overflow-hidden border border-gray-200 shadow-sm relative">
      <MapContainer
        center={center}
        zoom={13}
        zoomControl={false}   // We use custom ZoomControl placement below
        style={{ height: '100%', width: '100%', background: '#f9fafb' }}
      >
        {/* CartoDB Positron — clean, ultra-minimal light tile layer */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
          maxZoom={19}
        />

        {/* Place zoom controls in bottom-left to avoid FAB overlap */}
        <ZoomControl position="bottomleft" />

        {/* Render a marker for each real ticket from Firestore */}
        {issues.map((ticket) => {
          const severityLevel = ticket?.agent1_assessment?.severity_level ?? 3;
          return (
            <Marker
              key={ticket.ticket_id}
              position={[ticket.latitude, ticket.longitude]}
              icon={createIssueMarker(severityLevel)}
              eventHandlers={{
                click: () => onMarkerClick(ticket),
              }}
            />
          );
        })}
      </MapContainer>

      {/* Live ticket count badge overlay */}
      {issues.length > 0 && (
        <div className="absolute top-4 left-4 z-[400] bg-white/90 backdrop-blur-sm border border-gray-100 rounded-xl px-3 py-2 shadow-sm flex items-center gap-2">
          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
          <span className="text-xs font-semibold text-slate-700">{issues.length} Active Reports</span>
        </div>
      )}
    </div>
  );
};

export default MapFeed;
