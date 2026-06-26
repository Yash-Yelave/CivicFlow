import React from 'react';
import { CheckCircle, AlertTriangle, AlertCircle } from 'lucide-react';

const StatusBadge = ({ status }) => {
  const getStatusStyles = () => {
    switch (status.toLowerCase()) {
      case 'resolved':
        return {
          bg: 'bg-status-resolved-bg',
          text: 'text-status-resolved-text',
          icon: <CheckCircle size={14} className="mr-1" />
        };
      case 'pending':
        return {
          bg: 'bg-status-pending-bg',
          text: 'text-status-pending-text',
          icon: <AlertTriangle size={14} className="mr-1" />
        };
      case 'critical':
      case 'severe':
        return {
          bg: 'bg-status-critical-bg',
          text: 'text-status-critical-text',
          icon: <AlertCircle size={14} className="mr-1" />
        };
      default:
        return {
          bg: 'bg-gray-100',
          text: 'text-gray-600',
          icon: null
        };
    }
  };

  const styles = getStatusStyles();

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${styles.bg} ${styles.text}`}>
      {styles.icon}
      {status}
    </span>
  );
};

export default StatusBadge;
