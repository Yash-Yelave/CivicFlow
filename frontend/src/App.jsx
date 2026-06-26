import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, BarChart3, ShieldAlert, Wifi, WifiOff } from 'lucide-react';

// Components
import MapFeed from './components/MapFeed';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import ReportFab from './components/ReportFab';
import ReportModal from './components/ReportModal';
import IssueDetailPanel from './components/IssueDetailPanel';

// API Service
import { getTickets } from './services/api';

function App() {
  const [activeTab, setActiveTab]         = useState('map');
  const [showReportModal, setShowReportModal] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [tickets, setTickets]             = useState([]);
  const [isLoadingTickets, setIsLoadingTickets] = useState(true);
  const [userPosition, setUserPosition]   = useState(null); // { lat, lng }
  const [backendOnline, setBackendOnline] = useState(null); // null = checking

  // ── Fetch real tickets from Firestore on mount ──────────────────────────
  useEffect(() => {
    const loadTickets = async () => {
      try {
        const data = await getTickets();
        setTickets(data.tickets || []);
        setBackendOnline(true);
      } catch {
        setBackendOnline(false);
        // Fall back to demo data so the UI is still usable for presentation
        setTickets([
          {
            ticket_id: 'demo-1',
            latitude: 28.6139,
            longitude: 77.2090,
            upvotes: 12,
            status: 'Pending',
            description: 'High pressure water main rupture near Sector 4 intersection.',
            agent1_assessment: {
              issue_title: 'Major Water Main Pipe Burst',
              category: 'Water Leak',
              severity_level: 5,
              visual_summary: 'Significant water flow detected on road surface indicating pipe failure.'
            },
            agent2_routing: {
              assigned_department: 'Water & Sanitation Department',
              ticket_priority: 'CRITICAL',
              recommended_action: 'Dispatch emergency repair crew immediately.',
              estimated_resolution_time: '4-6 hours'
            }
          },
          {
            ticket_id: 'demo-2',
            latitude: 28.6200,
            longitude: 77.2150,
            upvotes: 8,
            status: 'Pending',
            description: 'Complete loss of power to synchronized traffic signals.',
            agent1_assessment: {
              issue_title: 'Traffic Signal Network Failure',
              category: 'Streetlight',
              severity_level: 4,
              visual_summary: 'Multiple traffic lights dark across main arterial road.'
            },
            agent2_routing: {
              assigned_department: 'Electrical & Streetlight Department',
              ticket_priority: 'HIGH',
              recommended_action: 'Deploy traffic wardens and inspect grid relay box.',
              estimated_resolution_time: '24-48 hours'
            }
          },
          {
            ticket_id: 'demo-3',
            latitude: 28.6050,
            longitude: 77.2000,
            upvotes: 45,
            status: 'Pending',
            description: 'Deep longitudinal cracking on primary bridge support pillar.',
            agent1_assessment: {
              issue_title: 'Structural Bridge Crack — Critical',
              category: 'Structural Damage',
              severity_level: 5,
              visual_summary: 'Horizontal cracking visible on load-bearing column, indicating structural fatigue.'
            },
            agent2_routing: {
              assigned_department: 'Urban Planning Department',
              ticket_priority: 'CRITICAL',
              recommended_action: 'Immediately close bridge to traffic and deploy structural engineers.',
              estimated_resolution_time: 'Emergency response — 1-3 days'
            }
          }
        ]);
      } finally {
        setIsLoadingTickets(false);
      }
    };
    loadTickets();
  }, []);

  // ── Capture user's browser GPS on mount ─────────────────────────────────
  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setUserPosition({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => setUserPosition({ lat: 28.6139, lng: 77.2090 }) // Fallback: New Delhi
      );
    }
  }, []);

  // ── Handle new ticket submitted via ReportModal ──────────────────────────
  const handleReportSubmitted = (newTicket) => {
    setTickets((prev) => [newTicket, ...prev]);
    setSelectedIssue(newTicket); // Auto-open the detail panel for the new ticket
  };

  // ── Handle upvote from IssueDetailPanel ─────────────────────────────────
  const handleUpvote = (ticketId, newCount) => {
    setTickets((prev) =>
      prev.map((t) => t.ticket_id === ticketId ? { ...t, upvotes: newCount } : t)
    );
  };

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden" style={{ backgroundColor: '#F9FAFB' }}>

      {/* ── Hyper-Minimal Header ─────────────────────────────────────────── */}
      <header className="px-6 py-4 flex justify-between items-center bg-white/90 backdrop-blur-md border-b border-gray-100 z-50 sticky top-0">
        <div className="flex items-center gap-3">
          <div className="bg-slate-900 p-2 rounded-xl text-white">
            <ShieldAlert size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight leading-none">CivicFlow</h1>
            <span className="text-[0.65rem] font-bold text-slate-400 uppercase tracking-widest">
              Autonomous Triage
            </span>
          </div>
          {/* Backend status indicator */}
          {backendOnline !== null && (
            <div className={`hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${
              backendOnline
                ? 'bg-emerald-50 text-emerald-600'
                : 'bg-amber-50 text-amber-600'
            }`}>
              {backendOnline ? <Wifi size={12} /> : <WifiOff size={12} />}
              {backendOnline ? 'Live' : 'Demo Mode'}
            </div>
          )}
        </div>

        {/* Fluid Toggle Switch with layoutId animation */}
        <nav className="bg-slate-100 p-1 rounded-xl flex">
          {[
            { id: 'map',       label: 'Live Map Feed',      icon: <MapPin size={15} /> },
            { id: 'analytics', label: 'Predictive Insights', icon: <BarChart3 size={15} /> },
          ].map(({ id, label, icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors z-10 ${
                activeTab === id ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              {activeTab === id && (
                <motion.div
                  layoutId="nav-pill"
                  className="absolute inset-0 bg-white rounded-lg shadow-sm"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              <span className="relative z-10 flex items-center gap-2">
                {icon} {label}
              </span>
            </button>
          ))}
        </nav>
      </header>

      {/* ── View Container ───────────────────────────────────────────────── */}
      <main className="flex-1 relative">
        <AnimatePresence mode="wait">
          {activeTab === 'map' ? (
            <motion.div
              key="map-view"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="absolute inset-0 p-6"
            >
              {isLoadingTickets ? (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center space-y-3">
                    <div className="w-8 h-8 border-2 border-slate-300 border-t-slate-700 rounded-full animate-spin mx-auto" />
                    <p className="text-sm text-slate-500">Loading live ticket data...</p>
                  </div>
                </div>
              ) : (
                <MapFeed
                  issues={tickets}
                  onMarkerClick={setSelectedIssue}
                  userPosition={userPosition}
                />
              )}
            </motion.div>
          ) : (
            <motion.div
              key="analytics-view"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="absolute inset-0 p-6 overflow-y-auto"
            >
              <AnalyticsDashboard />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* ── Overlays ─────────────────────────────────────────────────────── */}
      <ReportFab onClick={() => setShowReportModal(true)} />

      <ReportModal
        isOpen={showReportModal}
        onClose={() => setShowReportModal(false)}
        onReportSubmitted={handleReportSubmitted}
        userPosition={userPosition}
      />

      <IssueDetailPanel
        issue={selectedIssue}
        isOpen={!!selectedIssue}
        onClose={() => setSelectedIssue(null)}
        onUpvote={handleUpvote}
      />
    </div>
  );
}

export default App;
