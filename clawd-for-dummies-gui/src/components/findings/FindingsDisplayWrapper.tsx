import { lazy, Suspense, memo } from 'react';
import { useViewModeStore } from '../../stores/viewModeStore';

// Lazy load both view components for code splitting (Vercel best practice: bundle-dynamic-imports)
const DevFindingsDisplay = lazy(() =>
  import('../views/DevView/DevFindingsDisplay').then(m => ({ default: m.DevFindingsDisplay }))
);
const UserFindingsDisplay = lazy(() =>
  import('../views/UserView/UserFindingsDisplay').then(m => ({ default: m.UserFindingsDisplay }))
);

// Loading fallback skeleton
function LoadingFallback() {
  return (
    <div className="mt-6 space-y-4">
      <div className="animate-pulse bg-elevated rounded-xl h-24" />
      <div className="animate-pulse bg-elevated rounded-xl h-48" />
      <div className="animate-pulse bg-elevated rounded-xl h-48" />
    </div>
  );
}

export const FindingsDisplayWrapper = memo(function FindingsDisplayWrapper() {
  const viewMode = useViewModeStore((state) => state.viewMode);

  return (
    <Suspense fallback={<LoadingFallback />}>
      {viewMode === 'dev' ? <DevFindingsDisplay /> : <UserFindingsDisplay />}
    </Suspense>
  );
});
