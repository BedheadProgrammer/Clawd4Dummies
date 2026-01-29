import { memo, useMemo, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Filter,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  PartyPopper
} from 'lucide-react';
import { Card } from '../../common/Card';
import { FindingTile } from './FindingTile';
import { PriorityInstallAlert } from './PriorityInstallAlert';
import { useScanStore } from '../../../stores/scanStore';
import { Finding, Severity } from '../../../types/finding';
import { USER_FRIENDLY_SEVERITY, isPriorityFinding } from '../../../utils/findingUtils';

// Severity display order
const SEVERITY_ORDER: readonly Severity[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'] as const;

// Friendly status messages based on findings
function getStatusMessage(findings: readonly Finding[]): {
  icon: typeof ShieldCheck;
  title: string;
  subtitle: string;
  color: string;
} {
  const criticalCount = findings.filter(f => f.severity === 'CRITICAL').length;
  const highCount = findings.filter(f => f.severity === 'HIGH').length;
  const totalIssues = findings.length;

  if (totalIssues === 0) {
    return {
      icon: PartyPopper,
      title: 'All Clear!',
      subtitle: 'No security issues were found on your system.',
      color: 'text-low',
    };
  }

  if (criticalCount > 0) {
    return {
      icon: AlertTriangle,
      title: `${criticalCount} urgent ${criticalCount === 1 ? 'issue' : 'issues'} found`,
      subtitle: 'These need your immediate attention to keep your system safe.',
      color: 'text-rose-400',
    };
  }

  if (highCount > 0) {
    return {
      icon: ShieldAlert,
      title: `${highCount} important ${highCount === 1 ? 'issue' : 'issues'} to address`,
      subtitle: 'Taking care of these soon will improve your security.',
      color: 'text-orange-400',
    };
  }

  return {
    icon: ShieldCheck,
    title: `${totalIssues} ${totalIssues === 1 ? 'item' : 'items'} to review`,
    subtitle: 'Your system is mostly secure. Consider these improvements when you have time.',
    color: 'text-amber-400',
  };
}

export const UserFindingsDisplay = memo(function UserFindingsDisplay() {
  const { scanResult, status, filterSeverity, setFilterSeverity } = useScanStore();

  // Filter handler with friendly labels
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

  // Get status message
  const statusInfo = getStatusMessage(filteredFindings);
  const StatusIcon = statusInfo.icon;

  // Group findings by severity for organized display
  const groupedFindings = useMemo(() => {
    const groups: Record<Severity, Finding[]> = {
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

  // Count findings that need priority attention (like "Not Installed")
  const priorityFindings = filteredFindings.filter(isPriorityFinding);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mt-6"
    >
      {/* Status Header Card */}
      <Card className="mb-6">
        <div className="flex items-center gap-5 py-2">
          <div className={`p-4 rounded-2xl bg-gradient-to-br from-elevated to-space-black ${statusInfo.color}`}>
            <StatusIcon className="w-10 h-10" />
          </div>
          <div className="flex-1">
            <h2 className={`text-2xl font-semibold ${statusInfo.color}`}>
              {statusInfo.title}
            </h2>
            <p className="text-text-secondary mt-1">
              {statusInfo.subtitle}
            </p>
          </div>

          {/* Filter Dropdown */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-text-secondary" />
            <select
              value={filterSeverity}
              onChange={handleFilterChange}
              className="bg-space-black border border-text-secondary/30 rounded-xl px-4 py-2 text-sm text-text-primary focus:outline-none focus:border-action-blue transition-colors"
            >
              <option value="ALL">All Issues ({allFindings.length})</option>
              {SEVERITY_ORDER.map(severity => {
                const count = allFindings.filter(f => f.severity === severity).length;
                if (count === 0) return null;
                return (
                  <option key={severity} value={severity}>
                    {USER_FRIENDLY_SEVERITY[severity].label} ({count})
                  </option>
                );
              })}
            </select>
          </div>
        </div>
      </Card>

      {/* No findings message */}
      {filteredFindings.length === 0 && (
        <Card>
          <div className="text-center py-12">
            <PartyPopper className="w-16 h-16 text-low mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-text-primary mb-2">
              {filterSeverity === 'ALL'
                ? 'Your system looks great!'
                : `No ${USER_FRIENDLY_SEVERITY[filterSeverity as Severity].label.toLowerCase()} issues`}
            </h3>
            <p className="text-text-secondary">
              {filterSeverity === 'ALL'
                ? 'No security concerns were found during the scan.'
                : 'Try viewing all issues or a different category.'}
            </p>
          </div>
        </Card>
      )}

      {/* Priority Items First (e.g., "Not Installed" message) - Dynamic Alert */}
      {priorityFindings.length > 0 && (
        <div className="mb-8 space-y-6">
          {priorityFindings.map((finding, index) => {
            // Check if there are more findings below this priority finding
            const hasMoreFindings = 
              index < priorityFindings.length - 1 || // More priority findings after this one
              Object.values(groupedFindings).some(findings => 
                findings.some(f => !isPriorityFinding(f)) // Regular findings exist
              );
            return (
              <PriorityInstallAlert 
                key={finding.id} 
                finding={finding} 
                hasMoreFindings={hasMoreFindings}
              />
            );
          })}
        </div>
      )}

      {/* Findings Grid by Severity */}
      {SEVERITY_ORDER.map((severity) => {
        // Filter out priority findings from regular display
        const findings = groupedFindings[severity].filter(f => !isPriorityFinding(f));
        if (findings.length === 0) return null;

        const config = USER_FRIENDLY_SEVERITY[severity];

        return (
          <div key={severity} className="mb-6">
            <div className="flex items-center gap-2 mb-4">
              <div className={`w-2 h-2 rounded-full ${
                severity === 'CRITICAL' ? 'bg-rose-500' :
                severity === 'HIGH' ? 'bg-orange-500' :
                severity === 'MEDIUM' ? 'bg-amber-500' :
                severity === 'LOW' ? 'bg-emerald-500' :
                'bg-slate-500'
              }`} />
              <h3 className={`text-lg font-semibold ${config.textColor}`}>
                {config.label}
              </h3>
              <span className="text-text-secondary text-sm">
                ({findings.length} {findings.length === 1 ? 'issue' : 'issues'})
              </span>
            </div>

            {/* Responsive grid: 1 column on mobile, 2 on larger screens */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {findings.map((finding, index) => (
                <motion.div
                  key={finding.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <FindingTile finding={finding} />
                </motion.div>
              ))}
            </div>
          </div>
        );
      })}
    </motion.div>
  );
});
