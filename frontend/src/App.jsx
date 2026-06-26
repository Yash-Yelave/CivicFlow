import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, BarChart3, ShieldAlert } from 'lucide-react';

// Components
import MapFeed from './components/MapFeed';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import ReportFab from './components/ReportFab';
import ReportModal from './components/ReportModal';
import IssueDetailPanel from './components/IssueDetailPanel';

// Dummy Data
const DUMMY_ISSUES = [
  {
    id: 1,
    title: 'Major Water Main Pipe Burst',
    category: 'Water Supply',
    severity: 'Severe',
    description: 'High pressure water main rupture near Sector 4 intersection. Significant localized flooding and potential foundation damage to nearby commercial structures reported.',
    lat: 28.6139,
    lng: 77.2090,
    upvotes: 12
  },
  {
    id: 2,
    title: 'Traffic Signal Network Failure',
    category: 'Power Grid',
    severity: 'Pending',
    description: 'Complete loss of power to synchronized traffic signals along Main Arterial Road. Creating severe congestion and accident risks.',
    lat: 28.6200,
    lng: 77.2150,
    upvotes: 8
  },
  {
    id: 3,
    title: 'Structural Bridge Crack',
    category: 'Infrastructure',
    severity: 'Critical',
    description: 'Deep longitudinal cracking observed on primary support pillar of Northbound Overpass. Immediate structural assessment required.',
    lat: 28.6050,
    lng: 77.2000,
    upvotes: 45
  }
];

function App() {
  const [activeTab, setActiveTab] = useState('map'); // 'map' or 'analytics'
  const [showReportModal, setShowReportModal] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState(null);

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden bg-workspace">
      
      {/* Hyper-Minimal Header */}
      <header className="px-6 py-4 flex justify-between items-center bg-white/80 backdrop-blur-md border-b border-gray-100 z-50 sticky top-0">
        <div className="flex items-center gap-3">
          <div className="bg-slate-900 p-2 rounded-xl text-white shadow-micro">
            <ShieldAlert size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight leading-none">CivicFlow</h1>
            <span className="text-[0.65rem] font-bold text-slate-400 uppercase tracking-widest">Autonomous Triage</span>
          </div>
        </div>

        {/* Fluid Toggle Switch */}
        <nav className="bg-slate-100 p-1 rounded-xl flex shadow-inner">
          <button 
            onClick={() => setActiveTab('map')}
            className={`relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors z-10 ${activeTab === 'map' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'}`}
          >
            {activeTab === 'map' && (
              <motion.div layoutId="nav-pill" className="absolute inset-0 bg-white rounded-lg shadow-sm" transition={{ type: 'spring', stiffness: 400, damping: 30 }} />
            )}
            <span className="relative z-10 flex items-center gap-2"><MapPin size={16} /> Live Map Feed</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('analytics')}
            className={`relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-colors z-10 ${activeTab === 'analytics' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'}`}
          >
            {activeTab === 'analytics' && (
              <motion.div layoutId="nav-pill" className="absolute inset-0 bg-white rounded-lg shadow-sm" transition={{ type: 'spring', stiffness: 400, damping: 30 }} />
            )}
            <span className="relative z-10 flex items-center gap-2"><BarChart3 size={16} /> Predictive Insights</span>
          </button>
        </nav>
      </header>

      {/* View Container */}
      <main className="flex-1 relative">
        <AnimatePresence mode="wait">
          {activeTab === 'map' ? (
            <motion.div
              key="map-view"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="absolute inset-0 p-6 flex flex-col md:flex-row gap-6"
            >
              <div className="flex-1 relative">
                <MapFeed issues={DUMMY_ISSUES} onMarkerClick={setSelectedIssue} />
              </div>
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

      {/* Overlays */}
      <ReportFab onClick={() => setShowReportModal(true)} />
      <ReportModal isOpen={showReportModal} onClose={() => setShowReportModal(false)} />
      <IssueDetailPanel issue={selectedIssue} isOpen={!!selectedIssue} onClose={() => setSelectedIssue(null)} />
      
    </div>
  );
}

export default App;
