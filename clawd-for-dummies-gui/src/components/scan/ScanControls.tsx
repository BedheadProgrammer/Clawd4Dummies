import { memo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Search, ChevronDown, Play } from 'lucide-react';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { ModuleSelector } from './ModuleSelector';
import { useScanner } from '../../hooks/useScanner';

export const ScanControls = memo(function ScanControls() {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const { isScanning, startScan } = useScanner();

  const handleQuickScan = () => {
    // For quick scan, we'd set only port+config modules
    startScan();
  };

  const handleFullScan = () => {
    startScan();
  };

  return (
    <Card className="mt-6">
      <h3 className="text-lg font-display font-semibold text-text-primary mb-4">
        Scan Options
      </h3>

      {/* Scan Mode Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {/* Quick Scan */}
        <motion.button
          onClick={handleQuickScan}
          disabled={isScanning}
          className="flex items-start gap-4 p-4 rounded-lg border-2 border-text-secondary/30 hover:border-action-blue/50 transition-all text-left disabled:opacity-50"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="p-3 bg-action-blue/10 rounded-lg">
            <Zap className="w-6 h-6 text-action-blue" />
          </div>
          <div>
            <h4 className="font-semibold text-text-primary">Quick Scan</h4>
            <p className="text-sm text-text-secondary">Port + Config only</p>
            <p className="text-xs text-text-secondary mt-1">~30 seconds</p>
          </div>
        </motion.button>

        {/* Full Scan */}
        <motion.button
          onClick={handleFullScan}
          disabled={isScanning}
          className="flex items-start gap-4 p-4 rounded-lg border-2 border-text-secondary/30 hover:border-action-blue/50 transition-all text-left disabled:opacity-50"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="p-3 bg-action-blue/10 rounded-lg">
            <Search className="w-6 h-6 text-action-blue" />
          </div>
          <div>
            <h4 className="font-semibold text-text-primary">Full Scan</h4>
            <p className="text-sm text-text-secondary">All Modules</p>
            <p className="text-xs text-text-secondary mt-1">~2 minutes</p>
          </div>
        </motion.button>
      </div>

      {/* Advanced Options Toggle */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors mb-4"
      >
        <ChevronDown
          className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
        />
        <span className="text-sm">Advanced: Select Modules</span>
      </button>

      {/* Module Selection */}
      <AnimatePresence>
        {showAdvanced && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <ModuleSelector />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Scan Button */}
      <div className="mt-6 flex justify-center">
        <Button
          size="lg"
          onClick={handleFullScan}
          disabled={isScanning}
          isLoading={isScanning}
          leftIcon={!isScanning ? <Play className="w-5 h-5" /> : undefined}
          className="px-12"
        >
          {isScanning ? 'Scanning...' : 'Start Security Scan'}
        </Button>
      </div>
    </Card>
  );
});
