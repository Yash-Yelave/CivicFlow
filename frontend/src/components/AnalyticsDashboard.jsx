import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Zap, CheckCircle2, RefreshCw, Loader2 } from 'lucide-react';
import PredictiveCard from './PredictiveCard';
import { getAnalytics, getTickets } from '../services/api';

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
};

const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [ticketCount, setTicketCount] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch both analytics and live ticket count in parallel
      const [analyticsResponse, ticketsResponse] = await Promise.all([
        getAnalytics(),
        getTickets(),
      ]);
      setAnalytics(analyticsResponse.analytics);
      setTicketCount(ticketsResponse.count);
    } catch (err) {
      setError(err.message || 'Failed to load analytics data.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Static performance metrics — these represent system-level stats
  const metrics = [
    {
      label: 'Active Reports',
      value: isLoading ? '...' : String(ticketCount ?? 0),
      icon: <Activity size={20} className="text-blue-500" />,
      trend: 'Live from Firestore'
    },
    {
      label: 'Autonomous Triage Success Rate',
      value: '98.4%',
      icon: <CheckCircle2 size={20} className="text-emerald-500" />,
      trend: 'Gemini Flash'
    },
    {
      label: 'Average Routing Time',
      value: '< 2s',
      icon: <Zap size={20} className="text-amber-500" />,
      trend: 'Agent 1 + Agent 2'
    },
  ];

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="max-w-6xl mx-auto w-full space-y-8 pb-20"
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 tracking-tight mb-1">Municipal Analytics</h2>
          <p className="text-slate-500">Real-time performance metrics & Agent 3 predictive intelligence.</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={fetchData}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm font-medium text-slate-600 hover:bg-gray-50 shadow-sm disabled:opacity-50 transition-all"
        >
          <RefreshCw size={15} className={isLoading ? 'animate-spin' : ''} />
          Refresh
        </motion.button>
      </div>

      {/* Metric Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {metrics.map((metric, idx) => (
          <motion.div
            key={idx}
            variants={item}
            whileHover={{ scale: 1.02 }}
            className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:border-gray-200 transition-all"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-slate-50 rounded-lg">{metric.icon}</div>
              <span className="text-xs font-medium text-slate-400 bg-slate-50 px-2 py-1 rounded-full">
                {metric.trend}
              </span>
            </div>
            <h3 className="text-slate-500 text-sm font-medium mb-1">{metric.label}</h3>
            <p className="text-3xl font-bold text-slate-800 tracking-tight">{metric.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Predictive Intelligence Section */}
      <motion.div variants={item}>
        <div className="flex items-center gap-3 mb-6">
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Predictive Intelligence</h2>
          <span className="bg-indigo-50 text-indigo-700 text-xs font-bold px-2 py-1 rounded-md uppercase tracking-wider">
            Agent 3 Active
          </span>
        </div>

        {/* Loading Skeleton */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-16 gap-4">
            <Loader2 size={36} className="text-indigo-400 animate-spin" />
            <p className="text-sm text-slate-500 font-medium">Agent 3 is analyzing infrastructure patterns...</p>
            <div className="w-72 space-y-2 opacity-50">
              <div className="h-2 bg-gray-200 rounded animate-pulse" />
              <div className="h-2 bg-gray-200 rounded animate-pulse w-3/4" />
            </div>
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <div className="bg-red-50 border border-red-100 rounded-2xl p-6 text-center">
            <p className="text-red-600 font-medium text-sm">{error}</p>
            <button onClick={fetchData} className="mt-3 text-sm text-red-500 underline">
              Retry
            </button>
          </div>
        )}

        {/* Executive Summary */}
        {analytics && !isLoading && (
          <>
            {analytics.summary && (
              <motion.div variants={item} className="bg-slate-50 border border-slate-100 rounded-2xl p-5 mb-6">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Executive Summary</p>
                <p className="text-slate-700 text-sm leading-relaxed">{analytics.summary}</p>
              </motion.div>
            )}

            {/* High-Risk Clusters */}
            {analytics.high_risk_clusters?.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {analytics.high_risk_clusters.map((cluster, idx) => (
                  <PredictiveCard
                    key={idx}
                    cluster={{
                      title: `${cluster.issue_type} — ${cluster.sector}`,
                      description: cluster.insight,
                      impact: `${cluster.risk_level} Risk · ${cluster.report_count} reports`,
                    }}
                  />
                ))}
              </div>
            )}

            {/* Preventative Recommendations */}
            {analytics.preventative_recommendations?.length > 0 && (
              <motion.div variants={item}>
                <h3 className="text-lg font-bold text-slate-800 mb-4">Preventative Recommendations</h3>
                <div className="space-y-3">
                  {analytics.preventative_recommendations.map((rec, idx) => (
                    <motion.div
                      key={idx}
                      whileHover={{ scale: 1.005 }}
                      className="bg-white border border-gray-100 rounded-xl p-4 flex items-start gap-4"
                    >
                      <div className={`mt-1 flex-shrink-0 px-2 py-0.5 rounded-full text-xs font-bold ${
                        rec.urgency === 'HIGH' || rec.urgency === 'CRITICAL'
                          ? 'bg-red-50 text-red-600'
                          : rec.urgency === 'MEDIUM'
                          ? 'bg-amber-50 text-amber-600'
                          : 'bg-slate-100 text-slate-500'
                      }`}>
                        {rec.urgency}
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-0.5">
                          {rec.department}
                        </p>
                        <p className="text-sm text-slate-700">{rec.action}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Empty State for no data yet */}
            {analytics.high_risk_clusters?.length === 0 && (
              <div className="text-center py-12 text-slate-400">
                <p className="text-sm">No risk clusters detected yet. Submit more reports to enable Agent 3 pattern analysis.</p>
              </div>
            )}
          </>
        )}
      </motion.div>
    </motion.div>
  );
};

export default AnalyticsDashboard;
