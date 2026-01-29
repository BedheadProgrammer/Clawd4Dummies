import { memo, useCallback } from 'react';
import { useScanStore } from '../../stores/scanStore';
import { Tooltip } from '../common/Tooltip';

export const ModuleSelector = memo(function ModuleSelector() {
  const { modules, toggleModule } = useScanStore();

  const handleToggle = useCallback((moduleId: string) => {
    toggleModule(moduleId);
  }, [toggleModule]);

  return (
    <div className="bg-space-black/50 rounded-lg p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {modules.map((module) => (
          <Tooltip key={module.id} content={module.description}>
            <label className="flex items-center gap-3 p-3 rounded-lg border border-text-secondary/20 hover:border-text-secondary/40 cursor-pointer transition-colors">
              <input
                type="checkbox"
                checked={module.enabled}
                onChange={() => handleToggle(module.id)}
                className="w-4 h-4 rounded border-text-secondary bg-space-black text-action-blue focus:ring-action-blue focus:ring-offset-space-black"
              />
              <span className="text-text-primary text-sm">{module.name}</span>
            </label>
          </Tooltip>
        ))}
      </div>
    </div>
  );
});
