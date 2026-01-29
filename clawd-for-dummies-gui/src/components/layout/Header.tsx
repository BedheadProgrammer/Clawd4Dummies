import { memo } from 'react';
import { Shield, Download } from 'lucide-react';
import { Button } from '../common/Button';
import { ViewModeToggle } from '../views/ViewModeToggle';
import { useScanStore } from '../../stores/scanStore';

export const Header = memo(function Header() {
  const { status, scanResult } = useScanStore();
  const hasResults = status === 'complete' && scanResult !== null;

  return (
    <header className="bg-elevated border-b border-text-secondary/20">
      <div className="container mx-auto px-4 py-4 max-w-6xl">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-action-blue/10 rounded-lg">
              <Shield className="w-6 h-6 text-action-blue" />
            </div>
            <div>
              <h1 className="text-xl font-display font-bold text-text-primary">
                ClawdForDummies
              </h1>
              <p className="text-sm text-text-secondary">Security Assessment Tool</p>
            </div>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center gap-4">
            {status === 'scanning' && (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-action-blue rounded-full animate-pulse" />
                <span className="text-sm text-text-secondary">Scanning...</span>
              </div>
            )}
            {status === 'complete' && scanResult && (
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  scanResult.riskLevel === 'CRITICAL' ? 'bg-critical' :
                  scanResult.riskLevel === 'HIGH' ? 'bg-high' :
                  scanResult.riskLevel === 'MEDIUM' ? 'bg-medium' :
                  'bg-low'
                }`} />
                <span className="text-sm text-text-secondary">
                  Scan Complete
                </span>
              </div>
            )}

            {/* View Mode Toggle */}
            <ViewModeToggle />

            {/* Export Action */}
            {hasResults && (
              <Button
                variant="secondary"
                size="sm"
                leftIcon={<Download className="w-4 h-4" />}
                onClick={() => {
                  // Scroll to export section
                  document.getElementById('export-section')?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                Export
              </Button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
});
