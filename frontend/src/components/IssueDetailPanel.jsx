import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, ShieldAlert, Clock, Info, Loader2, Building2, Zap, Droplets } from 'lucide-react';
import StatusBadge from './StatusBadge';
import { verifyTicket } from '../services/api';

// Map category strings to department icons
const CategoryIcon = ({ category }) => {
  const icons = {
    'Water Leak':        <Droplets size={14} className="text-blue-500" />,
    'Streetlight':       <Zap size={14} className="text-amber-500" />,
    'Structural Damage': <Building2 size={14} className="text-red-500" />,
  };
  return icons[category] || <ShieldAlert size={14} className="text-slate-500" />;
};

// Maps severity_level (1-5) → human-readable string for StatusBadge
const severityToStatus = (level) => {
  if (level >= 5) return 'Critical';
  if (level >= 4) return 'Severe';
  if (level >= 3) return 'Pending';
  return 'Resolved';
};

const IssueDetailPanel = ({ issue, isOpen, onClose, onUpvote }) => {
  const [isVerifying, setIsVerifying]   = useState(false);
  const [hasVerified, setHasVerified]   = useState(false);
  const [verifyError, setVerifyError]   = useState(null);

  const a1 = issue?.agent1_assessment || {};
  const a2 = issue?.agent2_routing    || {};
  const upvotes = issue?.upvotes ?? 0;

  const handleVerify = async () => {
    if (hasVerified || !issue?.ticket_id) return;
    setIsVerifying(true);
    setVerifyError(null);
    try {
      const result = await verifyTicket(issue.ticket_id);
      setHasVerified(true);
      // Propagate new count up to App.jsx state so other views update too
      if (onUpvote) onUpvote(issue.ticket_id, result.new_upvote_count);
    } catch (err) {
      setVerifyError('Could not verify. Please try again.');
    } finally {
      setIsVerifying(false);
    }
  };

  // Priority badge color mapping
  const priorityColor = {
    CRITICAL: 'bg-red-50 text-red-600',
    HIGH:     'bg-amber-50 text-amber-600',
    MEDIUM:   'bg-blue-50 text-blue-600',
    LOW:      'bg-slate-100 text-slate-500',
  };

  return (
    <AnimatePresence>
      {isOpen && issue && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-[400] sm:bg-slate-900/10"
          />
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 h-full w-full sm:w-[420px] bg-white shadow-[0_0_40px_-10px_rgba(0,0,0,0.15)] z-[500] flex flex-col border-l border-gray-100"
          >
            {/* ── Header ── */}
            <div className="p-6 border-b border-gray-100 flex justify-between items-start bg-white/90 backdrop-blur-md sticky top-0 z-10">
              <div>
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <StatusBadge status={severityToStatus(a1.severity_level)} />
                  <span className="flex items-center gap-1 text-xs text-slate-500 font-medium">
                    <CategoryIcon category={a1.category} />
                    {a1.category || 'Infrastructure'}
                  </span>
                </div>
                <h2 className="text-xl font-bold text-slate-800 leading-snug pr-8">
                  {a1.issue_title || 'Infrastructure Issue'}
                </h2>
              </div>
              <button
                onClick={onClose}
                className="p-2 bg-gray-50 hover:bg-gray-100 rounded-full text-gray-500 transition-colors flex-shrink-0"
              >
                <X size={20} />
              </button>
            </div>

            {/* ── Scrollable Content ── */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">

              {/* Issue Image Placeholder (real image shown when available) */}
              <div className="rounded-2xl overflow-hidden border border-gray-100 bg-gradient-to-br from-slate-100 to-slate-200 relative aspect-video flex items-center justify-center">
                {issue.image_url ? (
                  <img
                    src={issue.image_url}
                    alt={a1.issue_title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <ShieldAlert size={48} className="text-slate-300" />
                )}
                {a1.severity_level && (
                  <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm px-2.5 py-1 rounded-lg text-xs font-bold text-slate-700 shadow-sm">
                    Severity {a1.severity_level}/5
                  </div>
                )}
                <div className="absolute bottom-3 right-3 bg-white/90 backdrop-blur-sm px-2.5 py-1 rounded-lg text-xs font-semibold text-indigo-600 shadow-sm flex items-center gap-1">
                  <CheckCircle size={11} /> AI Assessed
                </div>
              </div>

              {/* Visual Summary */}
              {a1.visual_summary && (
                <p className="text-slate-600 text-sm leading-relaxed">{a1.visual_summary}</p>
              )}

              {/* User Description */}
              {issue.description && (
                <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                    Citizen Report
                  </p>
                  <p className="text-sm text-slate-700">{issue.description}</p>
                </div>
              )}

              {/* Department Routing Card */}
              {a2.assigned_department && (
                <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                      Routed to
                    </p>
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${priorityColor[a2.ticket_priority] || 'bg-slate-100 text-slate-500'}`}>
                      {a2.ticket_priority}
                    </span>
                  </div>
                  <p className="font-semibold text-slate-800 text-sm mb-1">{a2.assigned_department}</p>
                  <p className="text-xs text-slate-500">{a2.recommended_action}</p>
                  {a2.estimated_resolution_time && (
                    <p className="text-xs text-indigo-600 font-medium mt-2 flex items-center gap-1">
                      <Clock size={12} /> ETA: {a2.estimated_resolution_time}
                    </p>
                  )}
                </div>
              )}

              {/* Autonomous Triage Tracker */}
              <div className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
                <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
                  <Info size={16} className="text-indigo-500" /> Autonomous Triage Path
                </h3>
                <div className="space-y-4">
                  {[
                    {
                      label: 'Report Received',
                      sub:   'Auto-geolocated & logged in Firestore',
                      done:  true
                    },
                    {
                      label: 'Agent 1: Visual Assessment',
                      sub:   `"${a1.issue_title || 'Issue identified'}" — ${a1.severity_level}/5 severity`,
                      done:  true
                    },
                    {
                      label: 'Agent 2: Department Routing',
                      sub:   a2.assigned_department
                        ? `Ticket created for ${a2.assigned_department}`
                        : 'Pending routing...',
                      done:  !!a2.assigned_department,
                      active: !a2.assigned_department
                    },
                  ].map((step, idx) => (
                    <div key={idx} className="flex gap-3">
                      <div className={`mt-0.5 w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 ${
                        step.done ? 'bg-emerald-500' : step.active ? 'bg-indigo-500' : 'bg-gray-200'
                      }`}>
                        {step.done && <CheckCircle size={10} className="text-white" />}
                        {step.active && <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />}
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-slate-800">{step.label}</p>
                        <p className="text-xs text-slate-500 leading-snug">{step.sub}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Location */}
              <div className="text-xs text-slate-400 flex gap-2">
                <span>📍</span>
                <span>{issue.latitude?.toFixed(4)}, {issue.longitude?.toFixed(4)}</span>
              </div>
            </div>

            {/* ── Footer: Verify Button ── */}
            <div className="p-6 border-t border-gray-100 bg-white space-y-2">
              {verifyError && (
                <p className="text-xs text-red-500 text-center">{verifyError}</p>
              )}
              <motion.button
                whileHover={{ scale: hasVerified ? 1 : 1.02 }}
                whileTap={{ scale: hasVerified ? 1 : 0.98 }}
                onClick={handleVerify}
                disabled={hasVerified || isVerifying}
                className={`w-full py-3.5 rounded-xl font-semibold shadow-sm flex items-center justify-center gap-2 transition-all text-sm ${
                  hasVerified
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 cursor-default'
                    : 'bg-white border border-gray-200 text-slate-700 hover:bg-gray-50 hover:border-gray-300'
                }`}
              >
                {isVerifying ? (
                  <><Loader2 size={16} className="animate-spin" /> Verifying...</>
                ) : hasVerified ? (
                  <><CheckCircle size={16} /> Verified — Thank you!</>
                ) : (
                  <>
                    Verify this issue
                    <span className="ml-1 px-2 py-0.5 bg-gray-100 rounded-md text-xs font-bold">
                      {upvotes}
                    </span>
                  </>
                )}
              </motion.button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default IssueDetailPanel;
