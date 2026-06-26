import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Zap, CheckCircle2 } from 'lucide-react';
import PredictiveCard from './PredictiveCard';

const AnalyticsDashboard = () => {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
  };

  const metrics = [
    { label: 'Active Reports', value: '1,248', icon: <Activity size={20} className="text-blue-500" />, trend: '+12% vs last week' },
    { label: 'Autonomous Triage Success Rate', value: '98.4%', icon: <CheckCircle2 size={20} className="text-emerald-500" />, trend: 'Consistent' },
    { label: 'Average Routing Time', value: '< 2s', icon: <Zap size={20} className="text-amber-500" />, trend: '-0.3s improvement' },
  ];

  const predictions = [
    {
      id: 1,
      title: 'Water Infrastructure Vulnerability',
      description: 'Sector 4 shows high risk of water main failure based on 12 recurring minor leak reports over the past 48 hours and historical pressure data.',
      impact: 'High (Residential Zone)',
    },
    {
      id: 2,
      title: 'Power Grid Stress Detection',
      description: 'Anomalous load patterns detected in Downtown district. Predictive models indicate 85% probability of localized blackout during peak hours.',
      impact: 'Critical (Commercial Hub)',
    }
  ];

  return (
    <motion.div 
      variants={container}
      initial="hidden"
      animate="show"
      className="max-w-6xl mx-auto w-full space-y-8 pb-20"
    >
      <div>
        <h2 className="text-3xl font-bold text-slate-900 tracking-tight mb-2">Municipal Analytics</h2>
        <p className="text-slate-500">Real-time system performance and Agent 3 predictive insights.</p>
      </div>

      {/* Metric Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {metrics.map((metric, idx) => (
          <motion.div 
            key={idx}
            variants={item}
            whileHover={{ scale: 1.02 }}
            className="bg-white p-6 rounded-2xl shadow-micro border border-gray-100"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-slate-50 rounded-lg">
                {metric.icon}
              </div>
              <span className="text-xs font-medium text-slate-400 bg-slate-50 px-2 py-1 rounded-full">{metric.trend}</span>
            </div>
            <h3 className="text-slate-500 text-sm font-medium mb-1">{metric.label}</h3>
            <p className="text-3xl font-bold text-slate-800 tracking-tight">{metric.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Predictive Intelligence Section */}
      <motion.div variants={item} className="mt-12">
        <div className="flex items-center gap-3 mb-6">
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Predictive Intelligence</h2>
          <span className="bg-indigo-50 text-indigo-700 text-xs font-bold px-2 py-1 rounded-md uppercase tracking-wider">Agent 3 Active</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {predictions.map(pred => (
            <PredictiveCard key={pred.id} cluster={pred} />
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default AnalyticsDashboard;
