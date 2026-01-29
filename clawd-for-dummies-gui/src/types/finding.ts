export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export type Category =
  | 'PORT_EXPOSURE'
  | 'AUTHENTICATION'
  | 'CREDENTIALS'
  | 'CONFIGURATION'
  | 'PERMISSIONS'
  | 'NETWORK';

export interface RemediationStep {
  readonly step: number;
  readonly instruction: string;
  readonly code?: string;
  readonly filePath?: string;
}

export interface Finding {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly severity: Severity;
  readonly category: Category;
  readonly cvssScore: number;
  readonly location?: string;
  readonly remediation: string;
  readonly remediationSteps: readonly RemediationStep[];
  readonly references?: readonly string[];
  readonly fixPrompt?: string;
}

export const SEVERITY_CONFIG: Record<Severity, {
  color: string;
  bgColor: string;
  borderColor: string;
  indicator: string;
  label: string;
}> = {
  CRITICAL: {
    color: 'text-critical',
    bgColor: 'bg-critical/10',
    borderColor: 'border-critical',
    indicator: '🔴',
    label: 'Critical',
  },
  HIGH: {
    color: 'text-high',
    bgColor: 'bg-high/10',
    borderColor: 'border-high',
    indicator: '🟠',
    label: 'High',
  },
  MEDIUM: {
    color: 'text-medium',
    bgColor: 'bg-medium/10',
    borderColor: 'border-medium',
    indicator: '🟡',
    label: 'Medium',
  },
  LOW: {
    color: 'text-low',
    bgColor: 'bg-low/10',
    borderColor: 'border-low',
    indicator: '🟢',
    label: 'Low',
  },
  INFO: {
    color: 'text-info',
    bgColor: 'bg-info/10',
    borderColor: 'border-info',
    indicator: '⚪',
    label: 'Info',
  },
};
