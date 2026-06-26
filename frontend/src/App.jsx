import React, { useState } from 'react';
import { MapPin, AlertTriangle, BarChart3, Upload, CheckCircle, ShieldAlert, Sparkles } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('map'); // 'map' or 'analytics'
  const [showReportModal, setShowReportModal] = useState(false);

  return (
    <div className="app-container" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#0b0f19' }}>
      
      {/* Premium Header */}
      <header className="glass-panel" style={{
        margin: '1rem',
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        position: 'sticky',
        top: '1rem',
        zIndex: 100
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
            padding: '0.5rem',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <ShieldAlert size={24} color="white" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0, letterSpacing: '-0.025em' }}>
              <span className="gradient-text">CivicFlow</span>
            </h1>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginTop: '-2px' }}>
              Autonomous Municipal Triage
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', gap: '0.5rem' }}>
          <button 
            className={`btn ${activeTab === 'map' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('map')}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem' }}
          >
            <MapPin size={18} />
            Live Map
          </button>
          <button 
            className={`btn ${activeTab === 'analytics' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('analytics')}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem' }}
          >
            <BarChart3 size={18} />
            AI Insights
          </button>
        </nav>
      </header>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '0 1rem 1rem 1rem', display: 'flex', flexDirection: 'column', position: 'relative' }}>
        
        {activeTab === 'map' ? (
          /* Live Map View */
          <div style={{ display: 'flex', flex: 1, gap: '1rem', height: 'calc(100vh - 180px)', minHeight: '500px' }}>
            
            {/* Sidebar list of issues */}
            <div className="glass-panel" style={{ width: '380px', display: 'flex', flexDirection: 'column', padding: '1.25rem', overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Active Reports</h2>
                <span className="glass-panel" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', color: 'var(--color-primary)', borderColor: 'var(--color-primary)' }}>
                  3 Issues Listed
                </span>
              </div>

              {/* Sample Issue Cards */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div className="glass-panel" style={{ padding: '1rem', cursor: 'pointer', transition: 'var(--transition-fast)', background: 'rgba(255,255,255,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--status-high)', background: 'rgba(239, 68, 68, 0.15)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                      Severe
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Water Supply</span>
                  </div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.25rem' }}>Major Water Main Pipe Burst</h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>Sector 4, near Main Junction. Flooding road and causing traffic.</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    <span>📍 28.6139, 77.2090</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--color-accent)' }}>
                      <CheckCircle size={12} /> 12 Upvotes
                    </span>
                  </div>
                </div>

                <div className="glass-panel" style={{ padding: '1rem', cursor: 'pointer', transition: 'var(--transition-fast)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--status-medium)', background: 'rgba(245, 158, 11, 0.15)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                      Medium
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Public Works</span>
                  </div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.25rem' }}>Deep Pothole</h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>Right lane after the metro pillar 128. Hazard for two-wheelers.</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    <span>📍 28.6145, 77.2098</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--color-accent)' }}>
                      <CheckCircle size={12} /> 5 Upvotes
                    </span>
                  </div>
                </div>
              </div>

              {/* Floating Report Button */}
              <button 
                className="btn btn-primary"
                onClick={() => setShowReportModal(true)}
                style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', width: '100%' }}
              >
                <AlertTriangle size={18} />
                Report New Issue
              </button>
            </div>

            {/* Map Container Viewport */}
            <div className="glass-panel" style={{ flex: 1, position: 'relative', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#131824', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', zIndex: 10, top: '1rem', right: '1rem' }} className="glass-panel">
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--color-accent)', display: 'inline-block' }}></span>
                  Map Feed Active (Leaflet Mode)
                </span>
              </div>
              
              {/* Fallback styling for mockup mapping representation */}
              <div style={{ textAlign: 'center', padding: '2rem' }}>
                <MapPin size={48} color="var(--color-primary)" style={{ animation: 'bounce 2s infinite' }} />
                <h3 style={{ fontSize: '1.25rem', marginTop: '1rem', fontWeight: 600 }}>Interactive Map View</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: '360px', margin: '0.5rem auto' }}>
                  Select issues from the left panel to highlight details, or tap "Report New Issue" to flag a location.
                </p>
              </div>
            </div>

          </div>
        ) : (
          /* AI Insights View */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '1000px', margin: '0 auto', width: '100%' }}>
            
            {/* Header section with sparkles */}
            <div className="glass-panel" style={{ padding: '2rem', display: 'flex', gap: '1.5rem', alignItems: 'center', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%)' }}>
              <div style={{
                background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                padding: '0.75rem',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Sparkles size={32} color="white" />
              </div>
              <div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.25rem' }}><span className="gradient-text">Predictive Analytics Platform</span></h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                  Gemini 1.5 Flash (Agent 3) runs periodic clustered assessments on active reports to suggest structural resolutions.
                </p>
              </div>
            </div>

            {/* AI Insights Card */}
            <div className="glass-panel" style={{ padding: '2rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Sparkles size={18} color="var(--color-secondary)" />
                Latest Prediction Run (Agent 3 Analysis)
              </h3>
              <div style={{ borderLeft: '3px solid var(--color-primary)', paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <h4 style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '1.05rem', marginBottom: '0.25rem' }}>
                    🚨 Infrastructure Fragility Alert: Sector 4 Water Main
                  </h4>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    <strong>Observation:</strong> Clustered reports of minor seepage, road surface wetness, and pipe leaks within a 150m radius of Sector 4.
                    <br />
                    <strong>AI Recommendation:</strong> Schedule system integrity pressure checks on Sector 4 primary pipelines. High risk of complete pipe burst within 14 days.
                  </p>
                </div>
                <div>
                  <h4 style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '1.05rem', marginBottom: '0.25rem' }}>
                    💡 Lighting Optimization Target: Sector 9 Metro Corridor
                  </h4>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    <strong>Observation:</strong> 4 reports of dark spots and broken streetlights near the Sector 9 metro stairs.
                    <br />
                    <strong>AI Recommendation:</strong> Dispatch Municipal Electrical Crew to replace high-pressure sodium bulbs with high-durability LEDs along the corridor.
                  </p>
                </div>
              </div>
            </div>

          </div>
        )}

      </main>

      {/* Simple Citizen Report Drawer / Modal Overlay */}
      {showReportModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0,0,0,0.6)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div className="glass-panel" style={{ width: '450px', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Report an Issue</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: 0 }}>
              Upload a photo or video of the local issue. The AI agent will auto-classify categories, severity, and route reports to the responsible department.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-primary)' }}>Upload Media (Image / Video)</label>
              <div style={{
                border: '2px dashed var(--border-color)',
                borderRadius: '8px',
                padding: '2rem',
                textAlign: 'center',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.5rem',
                transition: 'var(--transition-fast)'
              }}>
                <Upload size={32} color="var(--text-muted)" />
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Click to select media or drag here</span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-primary)' }}>Additional Details</label>
              <textarea 
                rows="3" 
                placeholder="Optional description of the issue..."
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  backgroundColor: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  color: 'white',
                  fontFamily: 'var(--font-family)',
                  fontSize: '0.9rem'
                }}
              />
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
              <button className="btn btn-secondary" onClick={() => setShowReportModal(false)} style={{ flex: 1 }}>
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={() => {
                  alert("Report submitted! The AI Assessor is inspecting your file.");
                  setShowReportModal(false);
                }}
                style={{ flex: 1 }}
              >
                Submit Report
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;
