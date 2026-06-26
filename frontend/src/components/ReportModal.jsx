import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, UploadCloud, MapPin, Loader2 } from 'lucide-react';

const ReportModal = ({ isOpen, onClose }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    // Simulate AI processing
    setTimeout(() => {
      setIsSubmitting(false);
      onClose();
    }, 2000);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-[1001]"
          />
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-0 left-0 right-0 md:left-auto md:right-4 md:bottom-4 md:top-auto md:w-[400px] bg-white rounded-t-3xl md:rounded-3xl shadow-elevated z-[1002] overflow-hidden flex flex-col max-h-[90vh]"
          >
            <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-white/50 backdrop-blur-md sticky top-0">
              <h2 className="text-xl font-semibold text-slate-800 tracking-tight">New Report</h2>
              <button onClick={onClose} className="p-2 bg-gray-50 hover:bg-gray-100 rounded-full text-gray-500 transition-colors">
                <X size={20} />
              </button>
            </div>

            <div className="p-6 overflow-y-auto">
              {isSubmitting ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-4">
                  <div className="relative">
                    <div className="absolute inset-0 border-4 border-indigo-100 rounded-full"></div>
                    <Loader2 size={48} className="text-indigo-600 animate-spin relative" />
                  </div>
                  <p className="text-sm font-medium text-slate-600">AI Agents Processing Image & Location...</p>
                  <div className="w-full space-y-2 mt-4 opacity-50">
                    <div className="h-2 bg-gray-200 rounded animate-pulse w-full"></div>
                    <div className="h-2 bg-gray-200 rounded animate-pulse w-3/4"></div>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Image Dropzone */}
                  <div className="border-2 border-dashed border-gray-200 rounded-2xl p-8 flex flex-col items-center justify-center text-center hover:bg-gray-50 hover:border-indigo-300 transition-colors cursor-pointer group">
                    <div className="w-12 h-12 bg-indigo-50 text-indigo-500 rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                      <UploadCloud size={24} />
                    </div>
                    <p className="text-sm font-medium text-slate-700">Drag & drop issue image</p>
                    <p className="text-xs text-slate-500 mt-1">PNG, JPG up to 10MB</p>
                  </div>

                  {/* Auto Geolocation */}
                  <div className="bg-slate-50 rounded-xl p-4 flex items-center gap-3 border border-slate-100">
                    <div className="p-2 bg-white rounded-lg shadow-micro text-emerald-500">
                      <MapPin size={18} />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Detected Location</p>
                      <p className="text-sm font-medium text-slate-800">40.7128° N, 74.0060° W</p>
                    </div>
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Description</label>
                    <textarea 
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none h-24"
                      placeholder="Briefly describe the infrastructure issue..."
                    />
                  </div>

                  <motion.button
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    className="w-full bg-slate-900 text-white font-medium py-3 rounded-xl hover:bg-slate-800 transition-colors shadow-micro"
                  >
                    Submit to AI Triage
                  </motion.button>
                </form>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default ReportModal;
