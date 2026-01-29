import { memo, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Filter } from 'lucide-react';
import { Card } from '../common/Card';
import { FindingCard } from './FindingCard';
import { useScanStore } from '../../stores/scanStore';
import { Severity, SEVERITY_CONFIG } from '../../types/finding';
import { staggerContainer } from '../../utils/animations';

// REACT BEST PRACTICE: Hoist static data outside component
const SEVERITY_ORDER: readonly Severity[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'] as const;

const SEVERITY_MESSAGES: Readonly<Record<Severity, string>> = {
  CRITICAL: 'Fix IMMEDIATELY',
  HIGH: 'Fix within 24 hours',
  MEDIUM: 'Fix within 1 week',
  LOW: 'Fix when convenient',
  INFO: 'Informational only',
} as const;

export const FindingsDisplay = memo(function FindingsDisplay() {
  const { scanResult, status, filterSeverity, setFilterSeverity, getFilteredFindings } = useScanStore();

  // Don't show if no results
  if (status !== 'complete' || !scanResult) return null;

  const filteredFindings = getFilteredFindings();

  // REACT BEST PRACTICE (rerender-memo): Memoize grouped findings
  const groupedFindings = useMemo(() => {
    const groups: Record<Severity, typeof filteredFindings> = {
      CRITICAL: [],
      HIGH: [],
      MEDIUM: [],
      LOW: [],
      INFO: [],
    };

    filteredFindings.forEach((finding) => {
      groups[finding.severity].push(finding);
    });

    return groups;
  }, [filteredFindings]);

  // REACT BEST PRACTICE (rerender-functional-setstate): Use useCallback for event handlers
  const handleFilterChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    // TYPE SAFETY: Validate the value before setting
    if (value === 'ALL' || value === 'CRITICAL' || value === 'HIGH' || 
        value === 'MEDIUM' || value === 'LOW' || value === 'INFO') {
      setFilterSeverity(value);
    }
  }, [setFilterSeverity]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mt-6"
    >
      <Card>
        {/* Header with Filter */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-display font-semibold text-text-primary">
            Security Findings
          </h3>

          {/* Filter Dropdown */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-text-secondary" />
            <select
              value={filterSeverity}
              onChange={handleFilterChange}
              className="bg-space-black border border-text-secondary/30 rounded-lg px-3 py-1.5 text-sm text-text-primary focus:outline-none focus:border-action-blue"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical Only</option>
              <option value="HIGH">High Only</option>
              <option value="MEDIUM">Medium Only</option>
              <option value="LOW">Low Only</option>
              <option value="INFO">Info Only</option>
            </select>
          </div>
        </div>

        {/* No findings message */}
        {filteredFindings.length === 0 && (
          <div className="text-center py-8 text-text-secondary">
            {filterSeverity === 'ALL'
              ? 'No security issues found! Your system looks safe.'
              : `No ${filterSeverity.toLowerCase()} severity issues found.`}
          </div>
        )}

        {/* Findings by Severity Group */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {SEVERITY_ORDER.map((severity) => {
            const findings = groupedFindings[severity];
            if (findings.length === 0) return null;

            const config = SEVERITY_CONFIG[severity];

            return (
              <div key={severity}>
                <h4 className={`text-sm font-semibold uppercase tracking-wider mb-3 ${config.color}`}>
                  {config.indicator} {config.label} Issues ({findings.length}) - {SEVERITY_MESSAGES[severity]}
                </h4>
                <div className="space-y-3">
                  {findings.map((finding) => (
                    <FindingCard key={finding.id} finding={finding} />
                  ))}
                </div>
              </div>
            );
          })}
        </motion.div>
      </Card>
    </motion.div>
  );
});
