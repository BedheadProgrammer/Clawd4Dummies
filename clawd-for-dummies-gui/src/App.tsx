import { Suspense, lazy } from 'react';
import { AppShell } from './components/layout/AppShell';
import { RiskDashboard } from './components/dashboard/RiskDashboard';
import { ScanControls } from './components/scan/ScanControls';
import { ProgressIndicator } from './components/scan/ProgressIndicator';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { useScanStore } from './stores/scanStore';

// Lazy load heavy components
const FindingsDisplayWrapper = lazy(() =>
  import('./components/findings/FindingsDisplayWrapper').then((m) => ({ default: m.FindingsDisplayWrapper }))
);
const ExportPanel = lazy(() =>
  import('./components/export/ExportPanel').then((m) => ({ default: m.ExportPanel }))
);
const SystemInfo = lazy(() =>
  import('./components/system/SystemInfo').then((m) => ({ default: m.SystemInfo }))
);

// Loading fallback
function LoadingFallback() {
  return (
    <div className="animate-pulse bg-elevated rounded-lg h-48 mt-6" />
  );
}

function App() {
  const { status } = useScanStore();
  const isScanning = status === 'scanning';
  const hasResults = status === 'complete';

  return (
    <ErrorBoundary>
      <AppShell>
        {/* Risk Dashboard - Always visible */}
        <ErrorBoundary>
          <RiskDashboard />
        </ErrorBoundary>

        {/* Scan Controls or Progress Indicator */}
        <ErrorBoundary>
          {isScanning ? <ProgressIndicator /> : <ScanControls />}
        </ErrorBoundary>

        {/* Results sections - only show after scan complete */}
        {hasResults && (
          <ErrorBoundary>
            <Suspense fallback={<LoadingFallback />}>
              <FindingsDisplayWrapper />
              <ExportPanel />
              <SystemInfo />
            </Suspense>
          </ErrorBoundary>
        )}
      </AppShell>
    </ErrorBoundary>
  );
}

export default App;
