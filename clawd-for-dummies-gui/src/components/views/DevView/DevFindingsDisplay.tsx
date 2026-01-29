import { memo, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Filter, ChevronDown, ChevronRight, Copy, Check, ExternalLink } from 'lucide-react';
import { Card } from '../../common/Card';
import { PriorityAlert } from './PriorityAlert';
import { useScanStore } from '../../../stores/scanStore';
import { Finding, Severity, SEVERITY_CONFIG } from '../../../types/finding';
import {
  isPriorityFinding,
  sortFindingsForDevView,
  groupFindingsBySeverity,
  SEVERITY_PRIORITY
} from '../../../utils/findingUtils';
import { staggerContainer, staggerItem } from '../../../utils/animations';
import { useState } from 'react';

// Severity display order
const SEVERITY_ORDER: readonly Severity[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'] as const;

const SEVERITY_MESSAGES: Readonly<Record<Severity, string>> = {
  CRITICAL: 'Fix IMMEDIATELY',
  HIGH: 'Fix within 24 hours',
  MEDIUM: 'Fix within 1 week',
  LOW: 'Fix when convenient',
  INFO: 'Informational only',
} as const;

// Memoized finding card for dev view (terminal style)
const DevFindingCard = memo(function DevFindingCard({
  finding,
  isExpanded,
  onToggle
}: {
  finding: Finding;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const [copiedStep, setCopiedStep] = useState<number | null>(null);
  const config = SEVERITY_CONFIG[finding.severity];

  const handleCopyStep = useCallback(async (text: string, stepIndex: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedStep(stepIndex);
      setTimeout(() => setCopiedStep(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, []);

  return (
    <motion.div
      variants={staggerItem}
      className={`border-l-4 ${config.borderColor} ${config.bgColor} rounded-r-lg overflow-hidden`}
    >
      {/* Header - Always visible */}
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-white/5 transition-colors"
        aria-expanded={isExpanded}
      >
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-text-secondary flex-shrink-0" />
        ) : (
          <ChevronRight className="w-4 h-4 text-text-secondary flex-shrink-0" />
        )}

        <span className={`font-mono text-sm ${config.color}`}>
          [{finding.severity}]
        </span>

        <span className="flex-1 font-mono text-text-primary truncate">
          {finding.title}
        </span>

        {finding.cvssScore > 0 && (
          <span className={`text-xs font-mono px-2 py-0.5 rounded ${config.bgColor} ${config.color}`}>
            CVSS: {finding.cvssScore.toFixed(1)}
          </span>
        )}
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="border-t border-text-secondary/10"
        >
          <div className="p-4 space-y-4">
            {/* Description */}
            <p className="text-text-secondary font-mono text-sm leading-relaxed">
              {finding.description}
            </p>

            {/* Location */}
            {finding.location && (
              <div className="font-mono text-sm">
                <span className="text-text-secondary">Location: </span>
                <span className="text-action-blue">{finding.location}</span>
              </div>
            )}

            {/* Remediation Steps */}
            {finding.remediationSteps && finding.remediationSteps.length > 0 && (
              <div className="bg-space-black/50 rounded-lg p-4">
                <h4 className="text-text-primary font-mono font-semibold mb-3">
                  HOW TO FIX:
                </h4>
                <ol className="space-y-2">
                  {finding.remediationSteps.map((step, index) => (
                    <li key={index} className="flex items-start gap-2 font-mono text-sm">
                      <span className="text-action-blue">{step.step}.</span>
                      <div className="flex-1">
                        <span className="text-text-primary">{step.instruction}</span>
                        {step.code && (
                          <div className="mt-1 flex items-center gap-2">
                            <code className="bg-black/50 text-low px-2 py-1 rounded text-xs">
                              {step.code}
                            </code>
                            <button
                              onClick={() => handleCopyStep(step.code!, index)}
                              className="p-1 rounded hover:bg-white/10 transition-colors"
                              aria-label={`Copy: ${step.code}`}
                            >
                              {copiedStep === index ? (
                                <Check className="w-3 h-3 text-low" />
                              ) : (
                                <Copy className="w-3 h-3 text-text-secondary" />
                              )}
                            </button>
                          </div>
                        )}
                      </div>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* Reference Links */}
            {finding.references && finding.references.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {finding.references.map((link, index) => (
                  <a
                    key={index}
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-action-blue hover:text-action-blue/80 font-mono"
                  >
                    <ExternalLink className="w-3 h-3" />
                    Reference {index + 1}
                  </a>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
});

export const DevFindingsDisplay = memo(function DevFindingsDisplay() {
  const { scanResult, status, filterSeverity, setFilterSeverity, expandedFindings, toggleFinding } = useScanStore();

  // Filter handler
  const handleFilterChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    if (value === 'ALL' || value === 'CRITICAL' || value === 'HIGH' ||
        value === 'MEDIUM' || value === 'LOW' || value === 'INFO') {
      setFilterSeverity(value);
    }
  }, [setFilterSeverity]);

  // Don't show if no results
  if (status !== 'complete' || !scanResult) return null;

  const allFindings = scanResult.findings;

  // Apply filter
  const filteredFindings = filterSeverity === 'ALL'
    ? allFindings
    : allFindings.filter(f => f.severity === filterSeverity);

  // Separate priority findings from regular findings
  const priorityFindings = filteredFindings.filter(isPriorityFinding);
  const regularFindings = filteredFindings.filter(f => !isPriorityFinding(f));

  // Group regular findings by severity
  const groupedFindings = groupFindingsBySeverity(regularFindings);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mt-6"
    >
      <Card>
        {/* Terminal-style header */}
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-text-secondary/20">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-critical" />
              <div className="w-3 h-3 rounded-full bg-medium" />
              <div className="w-3 h-3 rounded-full bg-low" />
            </div>
            <h3 className="text-lg font-display font-semibold text-text-primary">
              SECURITY FINDINGS
            </h3>
          </div>

          {/* Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-text-secondary" />
            <select
              value={filterSeverity}
              onChange={handleFilterChange}
              className="bg-space-black border border-text-secondary/30 rounded-lg px-3 py-1.5 text-sm text-text-primary font-mono focus:outline-none focus:border-action-blue"
            >
              <option value="ALL">All ({allFindings.length})</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
              <option value="INFO">Info</option>
            </select>
          </div>
        </div>

        {/* Priority Alerts - ALWAYS FIRST (Bright Red, Impossible to Miss) */}
        {priorityFindings.length > 0 && (
          <div className="mb-6 space-y-4">
            {priorityFindings.map((finding) => (
              <PriorityAlert key={finding.id} finding={finding} />
            ))}
          </div>
        )}

        {/* No findings message */}
        {filteredFindings.length === 0 && (
          <div className="text-center py-8 text-text-secondary font-mono">
            {filterSeverity === 'ALL'
              ? '> No security issues found. System appears secure.'
              : `> No ${filterSeverity.toLowerCase()} severity issues found.`}
          </div>
        )}

        {/* Regular Findings by Severity Group */}
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
                <h4 className={`text-sm font-mono uppercase tracking-wider mb-3 ${config.color}`}>
                  {config.indicator} {config.label.toUpperCase()} ISSUES ({findings.length}) - {SEVERITY_MESSAGES[severity]}
                </h4>
                <div className="space-y-2">
                  {findings.map((finding) => (
                    <DevFindingCard
                      key={finding.id}
                      finding={finding}
                      isExpanded={expandedFindings.has(finding.id)}
                      onToggle={() => toggleFinding(finding.id)}
                    />
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
