import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, UploadCloud, MapPin, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { submitReport } from '../services/api';

// Triage steps shown during AI processing — mimics the real backend pipeline
const TRIAGE_STEPS = [
  { label: 'Uploading image to secure storage...', delay: 0 },
  { label: 'Agent 1: Analyzing infrastructure issue via Gemini Vision...', delay: 1500 },
  { label: 'Agent 2: Routing to correct municipal department...', delay: 4000 },
  { label: 'Saving ticket to database...', delay: 6000 },
];

const ReportModal = ({ isOpen, onClose, onReportSubmitted, userPosition }) => {
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  // Current GPS coordinates — from parent (App.jsx) or fallback to New Delhi
  const latitude  = userPosition?.lat  ?? 28.6139;
  const longitude = userPosition?.lng ?? 77.2090;

  const handleFileSelect = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files[0]);
  };

  const handleClose = () => {
    if (isSubmitting) return; // Prevent close during submission
    setImageFile(null);
    setImagePreview(null);
    setDescription('');
    setError(null);
    setCurrentStep(0);
    onClose();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!imageFile) {
      setError('Please attach an image of the issue before submitting.');
      return;
    }

    setError(null);
    setIsSubmitting(true);

    // Animate through the triage steps in sync with expected processing time
    TRIAGE_STEPS.forEach((step, idx) => {
      setTimeout(() => setCurrentStep(idx), step.delay);
    });

    try {
      const result = await submitReport({
        imageFile,
        latitude,
        longitude,
        description,
      });

      // Notify parent (App.jsx) so the map can update with the new ticket
      if (onReportSubmitted) {
        onReportSubmitted(result.ticket);
      }
      handleClose();
    } catch (err) {
      setError(err.message || 'Submission failed. Please try again.');
    } finally {
      setIsSubmitting(false);
      setCurrentStep(0);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-[1001]"
          />
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-0 left-0 right-0 md:left-auto md:right-4 md:bottom-4 md:top-auto md:w-[420px] bg-white rounded-t-3xl md:rounded-3xl shadow-[0_20px_60px_-15px_rgba(0,0,0,0.2)] z-[1002] overflow-hidden flex flex-col max-h-[90vh]"
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-white/80 backdrop-blur-md sticky top-0">
              <div>
                <h2 className="text-xl font-bold text-slate-800 tracking-tight">Report Issue</h2>
                <p className="text-xs text-slate-400 mt-0.5">Powered by Gemini AI Multi-Agent System</p>
              </div>
              <button
                onClick={handleClose}
                disabled={isSubmitting}
                className="p-2 bg-gray-50 hover:bg-gray-100 rounded-full text-gray-500 transition-colors disabled:opacity-50"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-6 overflow-y-auto flex-1">
              {/* ── AI Processing State ── */}
              {isSubmitting ? (
                <div className="flex flex-col items-center justify-center py-10 space-y-6">
                  <div className="relative w-16 h-16">
                    <div className="absolute inset-0 border-4 border-indigo-100 rounded-full" />
                    <Loader2 size={64} className="text-indigo-500 animate-spin" />
                  </div>
                  <div className="w-full space-y-3">
                    {TRIAGE_STEPS.map((step, idx) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0.3 }}
                        animate={{ opacity: idx <= currentStep ? 1 : 0.3 }}
                        className="flex items-center gap-3"
                      >
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 transition-colors ${idx < currentStep ? 'bg-emerald-500' : idx === currentStep ? 'bg-indigo-500' : 'bg-gray-200'}`}>
                          {idx < currentStep ? (
                            <CheckCircle size={12} className="text-white" />
                          ) : (
                            <div className={`w-2 h-2 rounded-full ${idx === currentStep ? 'bg-white animate-pulse' : 'bg-gray-400'}`} />
                          )}
                        </div>
                        <p className={`text-sm transition-colors ${idx === currentStep ? 'text-slate-800 font-medium' : idx < currentStep ? 'text-emerald-600' : 'text-slate-400'}`}>
                          {step.label}
                        </p>
                      </motion.div>
                    ))}
                  </div>
                  <div className="w-full space-y-2 opacity-40">
                    <div className="h-2 bg-gray-200 rounded-full animate-pulse" />
                    <div className="h-2 bg-gray-200 rounded-full animate-pulse w-3/4" />
                  </div>
                </div>
              ) : (
                /* ── Report Form ── */
                <form onSubmit={handleSubmit} className="space-y-5">
                  {/* Error Alert */}
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: -8 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center gap-2 bg-red-50 border border-red-100 text-red-700 px-4 py-3 rounded-xl text-sm"
                    >
                      <AlertCircle size={16} className="flex-shrink-0" />
                      {error}
                    </motion.div>
                  )}

                  {/* Image Dropzone */}
                  <div
                    onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`border-2 border-dashed rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-all ${
                      isDragging ? 'border-indigo-400 bg-indigo-50' :
                      imagePreview ? 'border-emerald-300 bg-emerald-50/50' :
                      'border-gray-200 hover:bg-gray-50 hover:border-indigo-300'
                    }`}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => handleFileSelect(e.target.files[0])}
                    />
                    {imagePreview ? (
                      <div className="relative w-full">
                        <img src={imagePreview} alt="Preview" className="w-full max-h-40 object-cover rounded-xl" />
                        <div className="absolute top-2 right-2 bg-emerald-500 text-white p-1 rounded-full">
                          <CheckCircle size={14} />
                        </div>
                        <p className="text-xs text-emerald-600 font-medium mt-2">{imageFile?.name}</p>
                      </div>
                    ) : (
                      <>
                        <div className="w-12 h-12 bg-indigo-50 text-indigo-500 rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                          <UploadCloud size={24} />
                        </div>
                        <p className="text-sm font-medium text-slate-700">Drag & drop issue image</p>
                        <p className="text-xs text-slate-400 mt-1">PNG, JPG, HEIC up to 10MB</p>
                      </>
                    )}
                  </div>

                  {/* Auto Geolocation */}
                  <div className="bg-slate-50 rounded-xl p-4 flex items-center gap-3 border border-slate-100">
                    <div className="p-2 bg-white rounded-lg shadow-sm text-emerald-500">
                      <MapPin size={18} />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Auto-detected Location</p>
                      <p className="text-sm font-mono font-medium text-slate-800">
                        {latitude.toFixed(4)}°, {longitude.toFixed(4)}°
                      </p>
                    </div>
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Description <span className="text-slate-400 font-normal">(optional)</span>
                    </label>
                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition-all resize-none h-24"
                      placeholder="e.g., Large pothole causing traffic near the junction..."
                    />
                  </div>

                  <motion.button
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    disabled={!imageFile}
                    className="w-full bg-slate-900 text-white font-semibold py-3.5 rounded-xl hover:bg-slate-800 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Submit to AI Triage System
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
