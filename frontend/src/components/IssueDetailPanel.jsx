import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, ShieldAlert, Clock, Info } from 'lucide-react';
import StatusBadge from './StatusBadge';

const IssueDetailPanel = ({ issue, isOpen, onClose }) => {
  const [verifyCount, setVerifyCount] = useState(issue?.upvotes || 0);
  const [hasVerified, setHasVerified] = useState(false);

  const handleVerify = () => {
    if (!hasVerified) {
      setVerifyCount(c => c + 1);
      setHasVerified(true);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && issue && (
        <>
          {/* Backdrop for mobile, invisible on desktop but prevents clicks underneath if wanted, or we can just float it */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-[400] bg-transparent sm:bg-slate-900/10 backdrop-blur-sm sm:backdrop-blur-none"
          />
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 h-full w-full sm:w-[400px] bg-white shadow-elevated z-[500] flex flex-col border-l border-gray-100"
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-100 flex justify-between items-start bg-white/80 backdrop-blur-md">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <StatusBadge status={issue.severity} />
                  <span className="text-xs text-slate-500 font-medium tracking-wide">{issue.category}</span>
                </div>
                <h2 className="text-xl font-bold text-slate-800 leading-tight">{issue.title}</h2>
              </div>
              <button onClick={onClose} className="p-2 bg-gray-50 hover:bg-gray-100 rounded-full text-gray-500 transition-colors">
                <X size={20} />
              </button>
            </div>

            {/* Content Scroll */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Premium Image Card */}
              <div className="rounded-2xl overflow-hidden shadow-micro border border-gray-100 relative group bg-gray-50 aspect-video flex items-center justify-center">
                {/* Fallback pattern/placeholder if no image */}
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10 mix-blend-multiply"></div>
                <ShieldAlert size={48} className="text-gray-300 relative z-10" />
                <div className="absolute bottom-3 right-3 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-lg text-xs font-semibold text-slate-700 shadow-sm z-10">
                  AI Assessed
                </div>
              </div>

              <p className="text-slate-600 text-sm leading-relaxed">
                {issue.description}
              </p>

              {/* Triage Tracker */}
              <div className="bg-slate-50 rounded-2xl p-5 border border-slate-100">
                <h3 className="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
                  <Info size={16} className="text-indigo-500" /> Autonomous Triage Path
                </h3>
                <div className="space-y-4">
                  <div className="flex gap-3">
                    <div className="mt-1"><CheckCircle size={16} className="text-emerald-500" /></div>
                    <div>
                      <p className="text-sm font-medium text-slate-800">Report Received</p>
                      <p className="text-xs text-slate-500">Auto-geolocated & logged</p>
                    </div>
                  </div>
                  <div className="flex gap-3 relative before:content-[''] before:absolute before:left-2 before:top-[-16px] before:bottom-[20px] before:w-[2px] before:bg-emerald-200">
                    <div className="mt-1"><CheckCircle size={16} className="text-emerald-500 relative bg-slate-50" /></div>
                    <div>
                      <p className="text-sm font-medium text-slate-800">Agent 1: Visual Assessment</p>
                      <p className="text-xs text-slate-500">Confirmed structural damage (98% conf.)</p>
                    </div>
                  </div>
                  <div className="flex gap-3 relative before:content-[''] before:absolute before:left-2 before:top-[-16px] before:bottom-[20px] before:w-[2px] before:bg-indigo-200">
                    <div className="mt-1"><Clock size={16} className="text-indigo-500 relative bg-slate-50" /></div>
                    <div>
                      <p className="text-sm font-medium text-slate-800">Agent 2: Routing</p>
                      <p className="text-xs text-slate-500 text-indigo-600 font-medium">Ticket generated for Public Works</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer Action */}
            <div className="p-6 border-t border-gray-100 bg-white">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleVerify}
                disabled={hasVerified}
                className={`w-full py-3 rounded-xl font-medium shadow-micro flex items-center justify-center gap-2 transition-colors ${
                  hasVerified 
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 cursor-default' 
                    : 'bg-white border border-gray-200 text-slate-700 hover:bg-gray-50'
                }`}
              >
                {hasVerified ? (
                  <><CheckCircle size={18} /> Verified ({verifyCount})</>
                ) : (
                  <>Verify this issue <span className="ml-1 px-2 py-0.5 bg-gray-100 rounded-md text-xs font-bold">{verifyCount}</span></>
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
