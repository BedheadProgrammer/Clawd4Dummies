import { memo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Monitor, User, Shield, Globe, Clock } from 'lucide-react';
import { Card } from '../common/Card';
import { useScanStore } from '../../stores/scanStore';

export const SystemInfo = memo(function SystemInfo() {
  const [isExpanded, setIsExpanded] = useState(false);
  const { scanResult, status } = useScanStore();

  // Don't show if no results
  if (status !== 'complete' || !scanResult) return null;

  const { systemInfo, timestamp, durationSeconds } = scanResult;

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mt-6"
    >
      <Card>
        {/* Toggle Header */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center gap-2 text-left"
        >
          <ChevronDown
            className={`w-5 h-5 text-text-secondary transition-transform ${
              isExpanded ? 'rotate-180' : ''
            }`}
          />
          <span className="text-lg font-display font-semibold text-text-primary">
            System Information
          </span>
        </button>

        {/* Collapsible Content */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.25 }}
              className="overflow-hidden"
            >
              <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-4">
                {/* Platform */}
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-action-blue/10 rounded-lg">
                    <Monitor className="w-5 h-5 text-action-blue" />
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary uppercase tracking-wider">Platform</p>
                    <p className="text-text-primary font-medium">{systemInfo.platformDisplay}</p>
                  </div>
                </div>

                {/* User */}
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-action-blue/10 rounded-lg">
                    <User className="w-5 h-5 text-action-blue" />
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary uppercase tracking-wider">User</p>
                    <p className="text-text-primary font-medium">{systemInfo.username}</p>
                  </div>
                </div>

                {/* Privileges */}
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-action-blue/10 rounded-lg">
                    <Shield className="w-5 h-5 text-action-blue" />
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary uppercase tracking-wider">Privileges</p>
                    <p className={`font-medium ${systemInfo.isAdmin ? 'text-high' : 'text-text-primary'}`}>
                      {systemInfo.isAdmin ? 'Admin' : 'Standard User'}
                    </p>
                  </div>
                </div>

                {/* Python Version */}
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-action-blue/10 rounded-lg">
                    <span className="text-action-blue text-lg">🐍</span>
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary uppercase tracking-wider">Python</p>
                    <p className="text-text-primary font-medium">{systemInfo.pythonVersion}</p>
                  </div>
                </div>

                {/* Local IPs */}
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-action-blue/10 rounded-lg">
                    <Globe className="w-5 h-5 text-action-blue" />
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary uppercase tracking-wider">Local IPs</p>
                    <p className="text-text-primary font-medium font-mono text-sm">
                      {systemInfo.localIps.slice(0, 2).join(', ')}
                    </p>
                  </div>
                </div>

                {/* Scan Time */}
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-action-blue/10 rounded-lg">
                    <Clock className="w-5 h-5 text-action-blue" />
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary uppercase tracking-wider">Scan Time</p>
                    <p className="text-text-primary font-medium">{formatDate(timestamp)}</p>
                    <p className="text-xs text-text-secondary">
                      Duration: {durationSeconds.toFixed(2)}s
                    </p>
                  </div>
                </div>
              </div>

              {/* Privacy Notice */}
              <div className="mt-6 p-3 bg-low/10 border border-low/20 rounded-lg flex items-center gap-2">
                <span className="text-low">ℹ</span>
                <span className="text-sm text-text-secondary">
                  This scan was performed locally. No data was sent externally.
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
});
