import { memo, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastProps {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
  onClose: (id: string) => void;
}

export const Toast = memo(function Toast({
  id,
  type,
  message,
  duration = 3000,
  onClose,
}: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => onClose(id), 300);
    }, duration);

    return () => clearTimeout(timer);
  }, [id, duration, onClose]);

  const icons = {
    success: <CheckCircle className="w-5 h-5 text-low" />,
    error: <XCircle className="w-5 h-5 text-critical" />,
    warning: <AlertCircle className="w-5 h-5 text-medium" />,
    info: <Info className="w-5 h-5 text-action-blue" />,
  };

  const bgColors = {
    success: 'bg-low/10 border-low',
    error: 'bg-critical/10 border-critical',
    warning: 'bg-medium/10 border-medium',
    info: 'bg-action-blue/10 border-action-blue',
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 100 }}
          className={`flex items-center gap-3 p-4 rounded-lg border ${bgColors[type]} bg-elevated shadow-lg`}
        >
          {icons[type]}
          <span className="text-text-primary flex-1">{message}</span>
          <button
            onClick={() => {
              setIsVisible(false);
              setTimeout(() => onClose(id), 300);
            }}
            className="text-text-secondary hover:text-text-primary"
          >
            <X className="w-4 h-4" />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
});

// Toast container for managing multiple toasts
interface ToastContainerProps {
  toasts: Array<{ id: string; type: ToastType; message: string }>;
  onClose: (id: string) => void;
}

export const ToastContainer = memo(function ToastContainer({
  toasts,
  onClose,
}: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onClose={onClose} />
      ))}
    </div>
  );
});
