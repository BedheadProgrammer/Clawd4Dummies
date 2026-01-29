import { memo } from 'react';
import { Severity } from '../../../types/finding';
import { USER_FRIENDLY_SEVERITY } from '../../../utils/findingUtils';

interface SeverityPillProps {
  severity: Severity;
  className?: string;
}

export const SeverityPill = memo(function SeverityPill({ severity, className = '' }: SeverityPillProps) {
  const config = USER_FRIENDLY_SEVERITY[severity];

  return (
    <span
      className={`
        inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold
        ${config.bgColor} ${config.textColor} border ${config.borderColor}
        ${className}
      `}
    >
      {config.label}
    </span>
  );
});
