import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, ShieldAlert } from 'lucide-react';

const PredictiveCard = ({ cluster }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className="bg-white p-6 rounded-2xl shadow-micro border border-gray-100 hover:border-gray-200 hover:shadow-elevated transition-all duration-300"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
            <Sparkles size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-slate-800 text-lg tracking-tight">Agent 3 Prediction</h3>
            <span className="text-xs text-indigo-600 font-medium bg-indigo-50 px-2 py-0.5 rounded-full">High Confidence (94%)</span>
          </div>
        </div>
        <div className="text-red-500 bg-red-50 p-2 rounded-lg">
          <ShieldAlert size={20} />
        </div>
      </div>
      
      <div className="mb-6">
        <h4 className="text-slate-900 font-medium mb-2">{cluster.title}</h4>
        <p className="text-slate-600 text-sm leading-relaxed">
          {cluster.description}
        </p>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-xs text-slate-500">
          Impact: <span className="font-medium text-slate-700">{cluster.impact}</span>
        </div>
        <motion.button
          whileHover={{ x: 2 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center gap-2 bg-slate-900 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-slate-800 transition-colors"
        >
          Approve Prevention Order
          <ArrowRight size={16} />
        </motion.button>
      </div>
    </motion.div>
  );
};

export default PredictiveCard;
