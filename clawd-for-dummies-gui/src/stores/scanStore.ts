import { create } from 'zustand';
import { Finding, Severity } from '../types/finding';
import { ScanResult, ScanStatus, ScanModule, ScanProgress, DEFAULT_MODULES } from '../types/scan';

interface ScanStore {
  // State
  status: ScanStatus;
  scanResult: ScanResult | null;
  findings: Finding[];
  progress: ScanProgress[];
  modules: ScanModule[];
  expandedFindings: Set<string>;
  filterSeverity: Severity | 'ALL';
  error: string | null;

  // Actions
  setStatus: (status: ScanStatus) => void;
  setScanResult: (result: ScanResult) => void;
  setProgress: (progress: ScanProgress) => void;
  toggleModule: (moduleId: string) => void;
  toggleFinding: (findingId: string) => void;
  setFilterSeverity: (severity: Severity | 'ALL') => void;
  setError: (error: string | null) => void;
  reset: () => void;
  
  // Derived selectors
  getEnabledModules: () => string[];
  getFilteredFindings: () => Finding[];
  getCriticalCount: () => number;
  getHighCount: () => number;
  getMediumCount: () => number;
  getLowCount: () => number;
  getInfoCount: () => number;
}

// TYPE SAFETY: Use explicit typed initial state instead of 'as' assertions
const initialState: Pick<
  ScanStore,
  'status' | 'scanResult' | 'findings' | 'progress' | 'modules' | 'expandedFindings' | 'filterSeverity' | 'error'
> = {
  status: 'idle',
  scanResult: null,
  findings: [],
  progress: [],
  modules: [...DEFAULT_MODULES], // Create a new array to avoid mutation
  expandedFindings: new Set<string>(),
  filterSeverity: 'ALL',
  error: null,
};

// Create a fresh copy of initial state to avoid reference issues on reset
function getInitialState() {
  return {
    status: 'idle' as ScanStatus,
    scanResult: null as ScanResult | null,
    findings: [] as Finding[],
    progress: [] as ScanProgress[],
    modules: [...DEFAULT_MODULES],
    expandedFindings: new Set<string>(),
    filterSeverity: 'ALL' as const,
    error: null as string | null,
  };
}

export const useScanStore = create<ScanStore>((set, get) => ({
  ...getInitialState(),

  setStatus: (status) => set({ status }),

  setScanResult: (result) => set({
    scanResult: result,
    // TYPE SAFETY: Properly cast readonly array to mutable
    findings: [...result.findings],
    status: 'complete',
    progress: [],
  }),

  setProgress: (progressUpdate) => set((state) => {
    const existingIndex = state.progress.findIndex(p => p.module === progressUpdate.module);
    if (existingIndex >= 0) {
      const newProgress = [...state.progress];
      newProgress[existingIndex] = progressUpdate;
      return { progress: newProgress };
    }
    return { progress: [...state.progress, progressUpdate] };
  }),

  toggleModule: (moduleId) => set((state) => ({
    modules: state.modules.map(m =>
      m.id === moduleId ? { ...m, enabled: !m.enabled } : m
    ),
  })),

  toggleFinding: (findingId) => set((state) => {
    const newExpanded = new Set(state.expandedFindings);
    if (newExpanded.has(findingId)) {
      newExpanded.delete(findingId);
    } else {
      newExpanded.add(findingId);
    }
    return { expandedFindings: newExpanded };
  }),

  setFilterSeverity: (severity) => set({ filterSeverity: severity }),

  setError: (error) => set({ error, status: error ? 'error' : get().status }),

  // MEMORY LEAK FIX: Use getInitialState() to create fresh state objects
  reset: () => set(getInitialState()),

  getEnabledModules: () => get().modules.filter(m => m.enabled).map(m => m.id),

  getFilteredFindings: () => {
    const { findings, filterSeverity } = get();
    if (filterSeverity === 'ALL') return findings;
    return findings.filter(f => f.severity === filterSeverity);
  },

  getCriticalCount: () => get().findings.filter(f => f.severity === 'CRITICAL').length,
  getHighCount: () => get().findings.filter(f => f.severity === 'HIGH').length,
  getMediumCount: () => get().findings.filter(f => f.severity === 'MEDIUM').length,
  getLowCount: () => get().findings.filter(f => f.severity === 'LOW').length,
  getInfoCount: () => get().findings.filter(f => f.severity === 'INFO').length,
}));
