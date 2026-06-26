import React from 'react';
import { MapContainer, TileLayer, Marker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { renderToStaticMarkup } from 'react-dom/server';
import { AlertCircle, Zap, Droplets } from 'lucide-react';

// Custom icons based on severity/type
const createCustomIcon = (severity, type) => {
  let bgColor = 'bg-slate-800';
  let icon = <AlertCircle size={16} className="text-white" />;
  
  if (severity === 'Critical' || severity === 'Severe') bgColor = 'bg-red-500';
  else if (severity === 'Pending') bgColor = 'bg-amber-500';

  if (type === 'Water Supply') icon = <Droplets size={16} className="text-white" />;
  else if (type === 'Power Grid') icon = <Zap size={16} className="text-white" />;

  const html = renderToStaticMarkup(
    <div className={`w-8 h-8 ${bgColor} rounded-full flex items-center justify-center shadow-lg border-2 border-white transform transition-transform hover:scale-110`}>
      {icon}
    </div>
  );

  return L.divIcon({
    html,
    className: 'custom-leaflet-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

const MapFeed = ({ issues, onMarkerClick }) => {
  const center = [28.6139, 77.2090]; // Default center

  return (
    <div className="w-full h-full rounded-3xl overflow-hidden border border-gray-200 shadow-micro relative z-10">
      <MapContainer center={center} zoom={13} zoomControl={false} style={{ height: '100%', width: '100%' }}>
        {/* Minimalist Light Map Tiles (CartoDB Positron) */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        {issues.map((issue) => (
          <Marker
            key={issue.id}
            position={[issue.lat, issue.lng]}
            icon={createCustomIcon(issue.severity, issue.category)}
            eventHandlers={{
              click: () => onMarkerClick(issue),
            }}
          />
        ))}
      </MapContainer>
    </div>
  );
};

export default MapFeed;
