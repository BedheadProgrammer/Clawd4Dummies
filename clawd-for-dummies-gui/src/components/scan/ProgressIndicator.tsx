import { memo } from 'react';
import { motion } from 'framer-motion';
import { Check, Loader2, Circle, X } from 'lucide-react';
import { Card } from '../common/Card';
import { ProgressBar } from '../common/ProgressBar';
import { Button } from '../common/Button';
import { useScanStore } from '../../stores/scanStore';
import { useScanner } from '../../hooks/useScanner';
import { ScanProgress as ScanProgressType } from '../../types/scan';

interface ModuleStatusProps {
  module: { id: string; name: string };
  progress?: ScanProgressType;
}

const ModuleStatus = memo(function ModuleStatus({ module, progress }: ModuleStatusProps) {
  const status = progress?.status || 'pending';

  const statusIcons = {
    pending: <Circle className="w-4 h-4 text-text-secondary" />,
    in_progress: <Loader2 className="w-4 h-4 text-action-blue animate-spin" />,
    complete: <Check className="w-4 h-4 text-low" />,
    error: <X className="w-4 h-4 text-critical" />,
  };

  const statusText = {
    pending: 'Pending',
    in_progress: 'In Progress',
    complete: 'Complete',
    error: 'Error',
  };

  return (
    <div className="flex items-center justify-between py-2 border-b border-text-secondary/10 last:border-0">
      <span className="text-text-primary">{module.name}</span>
      <div className="flex items-center gap-2">
        {statusIcons[status]}
        <span className="text-sm text-text-secondary">{statusText[status]}</span>
      </div>
    </div>
  );
});

export const ProgressIndicator = memo(function ProgressIndicator() {
  const { modules, progress, status } = useScanStore();
  const { cancelScan, isScanning } = useScanner();

  if (!isScanning) return null;

  // Calculate overall progress
  const completedModules = progress.filter(p => p.status === 'complete').length;
  const totalModules = modules.filter(m => m.enabled).length;
  const overallProgress = totalModules > 0 ? (completedModules / totalModules) * 100 : 0;

  // Get current operation
  const currentModule = progress.find(p => p.status === 'in_progress');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="mt-6">
        <div className="text-center mb-6">
          <h3 className="text-lg font-display font-semibold text-text-primary flex items-center justify-center gap-2">
            <Loader2 className="w-5 h-5 text-action-blue animate-spin" />
            Scanning Your System
          </h3>
        </div>

        {/* Progress Bar */}
        <ProgressBar value={overallProgress} showLabel />

        {/* Module List */}
        <div className="mt-6">
          {modules.filter(m => m.enabled).map((module) => {
            const moduleProgress = progress.find(p => p.module === module.id);
            return (
              <ModuleStatus
                key={module.id}
                module={module}
                progress={moduleProgress}
              />
            );
          })}
        </div>

        {/* Current Operation */}
        {currentModule && (
          <div className="mt-4 text-center">
            <p className="text-sm text-text-secondary">
              Current: {currentModule.currentOperation || `Scanning ${currentModule.module}...`}
            </p>
          </div>
        )}

        {/* Cancel Button */}
        <div className="mt-6 flex justify-center">
          <Button
            variant="secondary"
            size="sm"
            onClick={cancelScan}
            leftIcon={<X className="w-4 h-4" />}
          >
            Cancel Scan
          </Button>
        </div>
      </Card>
    </motion.div>
  );
});
