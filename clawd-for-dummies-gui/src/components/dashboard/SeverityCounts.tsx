import { memo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useScanStore } from '../../stores/scanStore';
import { Severity, SEVERITY_CONFIG } from '../../types/finding';

interface SeverityCountsProps {
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

interface CountBadgeProps {
  severity: Severity;
  count: number;
  onClick: () => void;
  isActive: boolean;
}

const CountBadge = memo(function CountBadge({ severity, count, onClick, isActive }: CountBadgeProps) {
  const config = SEVERITY_CONFIG[severity];
  
  return (
    <motion.button
      onClick={onClick}
      className={`flex flex-col items-center p-4 rounded-lg border-2 transition-all ${
        isActive 
          ? `${config.bgColor} ${config.borderColor}` 
          : 'border-transparent hover:bg-elevated/50'
      }`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <span className="text-2xl mb-1">{config.indicator}</span>
      <span className={`text-2xl font-display font-bold ${config.color}`}>
        {count}
      </span>
      <span className="text-xs text-text-secondary uppercase tracking-wider">
        {config.label}
      </span>
    </motion.button>
  );
});

export const SeverityCounts = memo(function SeverityCounts({
  critical,
  high,
  medium,
  low,
  info,
}: SeverityCountsProps) {
  const { filterSeverity, setFilterSeverity } = useScanStore();

  const handleClick = useCallback((severity: Severity) => {
    setFilterSeverity(filterSeverity === severity ? 'ALL' : severity);
  }, [filterSeverity, setFilterSeverity]);

  return (
    <div className="flex flex-wrap justify-center gap-2 mt-8">
      <CountBadge
        severity="CRITICAL"
        count={critical}
        onClick={() => handleClick('CRITICAL')}
        isActive={filterSeverity === 'CRITICAL'}
      />
      <CountBadge
        severity="HIGH"
        count={high}
        onClick={() => handleClick('HIGH')}
        isActive={filterSeverity === 'HIGH'}
      />
      <CountBadge
        severity="MEDIUM"
        count={medium}
        onClick={() => handleClick('MEDIUM')}
        isActive={filterSeverity === 'MEDIUM'}
      />
      <CountBadge
        severity="LOW"
        count={low}
        onClick={() => handleClick('LOW')}
        isActive={filterSeverity === 'LOW'}
      />
      <CountBadge
        severity="INFO"
        count={info}
        onClick={() => handleClick('INFO')}
        isActive={filterSeverity === 'INFO'}
      />
    </div>
  );
});
