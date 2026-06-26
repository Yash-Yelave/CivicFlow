import React from 'react';
import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';

const ReportFab = ({ onClick }) => {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className="fixed bottom-8 right-8 w-14 h-14 bg-slate-900 text-white rounded-full flex items-center justify-center shadow-elevated z-[1000] hover:bg-slate-800 transition-colors"
      aria-label="New Report"
    >
      <Plus size={24} />
    </motion.button>
  );
};

export default ReportFab;
