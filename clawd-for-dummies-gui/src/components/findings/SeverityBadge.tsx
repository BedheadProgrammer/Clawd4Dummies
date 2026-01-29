import { memo } from 'react';
import { Severity, SEVERITY_CONFIG } from '../../types/finding';

interface SeverityBadgeProps {
  severity: Severity;
  score?: number;
  size?: 'sm' | 'md';
}

export const SeverityBadge = memo(function SeverityBadge({
  severity,
  score,
  size = 'md',
}: SeverityBadgeProps) {
  const config = SEVERITY_CONFIG[severity];

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ${sizeStyles[size]} ${config.bgColor} ${config.color}`}
    >
      <span>{config.indicator}</span>
      {score !== undefined && score > 0 && (
        <span className="font-mono">CVSS: {score.toFixed(1)}</span>
      )}
    </span>
  );
});
