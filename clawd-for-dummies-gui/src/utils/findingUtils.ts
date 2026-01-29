import { Finding, Severity } from '../types/finding';

// Priority finding ID from Python backend (clawdbot_security_scanner.py)
export const PRIORITY_FINDING_ID = 'CLAWD-INSTALL-001';

// Severity sort order (CRITICAL first)
export const SEVERITY_PRIORITY: Record<Severity, number> = {
  CRITICAL: 0,
  HIGH: 1,
  MEDIUM: 2,
  LOW: 3,
  INFO: 4,
} as const;

/**
 * Check if finding is a priority alert (fires first in dev view)
 * This includes the "Moltbot Not Installed" message
 */
export function isPriorityFinding(finding: Finding): boolean {
  return finding.id === PRIORITY_FINDING_ID ||
         finding.title.toLowerCase().includes('not installed') ||
         finding.title.toLowerCase().includes('not configured');
}

/**
 * Sort findings with priority messages first, then by severity
 * Used in Dev View for proper message ordering
 */
export function sortFindingsForDevView(findings: readonly Finding[]): Finding[] {
  const priority = findings.filter(isPriorityFinding);
  const regular = findings.filter(f => !isPriorityFinding(f));

  // Sort regular findings by severity
  const sortedRegular = [...regular].sort((a, b) =>
    SEVERITY_PRIORITY[a.severity] - SEVERITY_PRIORITY[b.severity]
  );

  return [...priority, ...sortedRegular]; // Priority FIRST
}

/**
 * Group findings by severity for display
 */
export function groupFindingsBySeverity(
  findings: readonly Finding[]
): Record<Severity, Finding[]> {
  const groups: Record<Severity, Finding[]> = {
    CRITICAL: [],
    HIGH: [],
    MEDIUM: [],
    LOW: [],
    INFO: [],
  };

  findings.forEach((finding) => {
    groups[finding.severity].push(finding);
  });

  return groups;
}

/**
 * User-friendly severity labels for the User View
 */
export const USER_FRIENDLY_SEVERITY: Record<Severity, {
  label: string;
  description: string;
  bgColor: string;
  textColor: string;
  borderColor: string;
}> = {
  CRITICAL: {
    label: 'Urgent',
    description: 'Needs immediate attention',
    bgColor: 'bg-rose-500/10',
    textColor: 'text-rose-400',
    borderColor: 'border-rose-500/30',
  },
  HIGH: {
    label: 'Important',
    description: 'Should be fixed soon',
    bgColor: 'bg-orange-500/10',
    textColor: 'text-orange-400',
    borderColor: 'border-orange-500/30',
  },
  MEDIUM: {
    label: 'Recommended',
    description: 'Worth addressing when you can',
    bgColor: 'bg-amber-500/10',
    textColor: 'text-amber-400',
    borderColor: 'border-amber-500/30',
  },
  LOW: {
    label: 'Optional',
    description: 'Nice to have improvements',
    bgColor: 'bg-emerald-500/10',
    textColor: 'text-emerald-400',
    borderColor: 'border-emerald-500/30',
  },
  INFO: {
    label: 'Good to Know',
    description: 'Just for your information',
    bgColor: 'bg-slate-500/10',
    textColor: 'text-slate-400',
    borderColor: 'border-slate-500/30',
  },
};
