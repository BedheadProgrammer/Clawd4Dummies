import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ViewMode = 'dev' | 'user';

interface ViewModeStore {
  viewMode: ViewMode;
  setViewMode: (mode: ViewMode) => void;
  toggleViewMode: () => void;
}

export const useViewModeStore = create<ViewModeStore>()(
  persist(
    (set) => ({
      viewMode: 'user', // Default to user-friendly view
      setViewMode: (mode) => set({ viewMode: mode }),
      toggleViewMode: () => set((state) => ({
        viewMode: state.viewMode === 'dev' ? 'user' : 'dev'
      })),
    }),
    {
      name: 'clawd-view-mode', // localStorage key
    }
  )
);
