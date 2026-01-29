import { memo } from 'react';
import { motion } from 'framer-motion';
import { Terminal, LayoutGrid } from 'lucide-react';
import { useViewModeStore } from '../../stores/viewModeStore';

interface ViewModeToggleProps {
  className?: string;
}

export const ViewModeToggle = memo(function ViewModeToggle({ className = '' }: ViewModeToggleProps) {
  const { viewMode, toggleViewMode } = useViewModeStore();
  const isDevMode = viewMode === 'dev';

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-xs text-text-secondary hidden sm:inline">View:</span>
      <button
        onClick={toggleViewMode}
        className="relative flex items-center bg-space-black border border-text-secondary/30 rounded-lg p-1 hover:border-action-blue/50 transition-colors focus:outline-none focus:ring-2 focus:ring-action-blue/50"
        aria-label={`Switch to ${isDevMode ? 'user-friendly' : 'developer'} view`}
        role="switch"
        aria-checked={isDevMode}
      >
        {/* Sliding background indicator */}
        <motion.div
          className="absolute h-7 w-7 bg-action-blue/20 rounded-md"
          initial={false}
          animate={{
            x: isDevMode ? 0 : 32,
          }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        />

        {/* Dev Mode Button */}
        <div
          className={`relative z-10 flex items-center justify-center w-7 h-7 rounded-md transition-colors ${
            isDevMode ? 'text-action-blue' : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          <Terminal className="w-4 h-4" />
        </div>

        {/* User Mode Button */}
        <div
          className={`relative z-10 flex items-center justify-center w-7 h-7 rounded-md transition-colors ${
            !isDevMode ? 'text-action-blue' : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          <LayoutGrid className="w-4 h-4" />
        </div>
      </button>

      {/* Mode label */}
      <span className="text-xs text-text-secondary min-w-[60px]">
        {isDevMode ? 'Dev' : 'Friendly'}
      </span>
    </div>
  );
});
