import { Finding, Severity } from './finding';

export type RiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'SAFE';

export interface SystemInfo {
  readonly platform: string;
  readonly platformDisplay: string;
  readonly pythonVersion: string;
  readonly username: string;
  readonly isAdmin: boolean;
  readonly localIps: readonly string[];
}

export interface ScanProgress {
  readonly module: string;
  readonly status: 'pending' | 'in_progress' | 'complete' | 'error';
  readonly percentage?: number;
  readonly currentOperation?: string;
}

export interface ScanResult {
  readonly scanId: string;
  readonly timestamp: string;
  readonly durationSeconds: number;
  readonly findings: readonly Finding[];
  readonly systemInfo: SystemInfo;
  readonly overallRiskScore: number;
  readonly riskLevel: RiskLevel;
  readonly criticalCount: number;
  readonly highCount: number;
  readonly mediumCount: number;
  readonly lowCount: number;
  readonly infoCount: number;
}

export type ScanStatus = 'idle' | 'scanning' | 'complete' | 'error';

export interface ScanModule {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly enabled: boolean;
}

export const DEFAULT_MODULES: ScanModule[] = [
  { id: 'port', name: 'Port Scanner', description: 'Check for exposed ports and authentication bypass', enabled: true },
  { id: 'credential', name: 'Credential Scanner', description: 'Scan for exposed API keys and tokens', enabled: true },
  { id: 'config', name: 'Config Analyzer', description: 'Validate Clawdbot configuration files', enabled: true },
  { id: 'process', name: 'Process Monitor', description: 'Check Clawdbot process security', enabled: true },
  { id: 'permission', name: 'File Permissions', description: 'Validate file permissions', enabled: true },
  { id: 'network', name: 'Network Analyzer', description: 'Analyze network exposure', enabled: true },
  { id: 'clawdbot', name: 'Clawdbot Scanner', description: 'Check Moltbot/Clawdbot security configurations', enabled: true },
];

export const RISK_LEVEL_CONFIG: Record<RiskLevel, {
  color: string;
  bgColor: string;
  label: string;
  message: string;
}> = {
  CRITICAL: {
    color: 'text-critical',
    bgColor: 'bg-critical',
    label: 'Critical Risk',
    message: 'Immediate action required!',
  },
  HIGH: {
    color: 'text-high',
    bgColor: 'bg-high',
    label: 'High Risk',
    message: 'Fix within 24 hours',
  },
  MEDIUM: {
    color: 'text-medium',
    bgColor: 'bg-medium',
    label: 'Medium Risk',
    message: 'Fix within 1 week',
  },
  LOW: {
    color: 'text-low',
    bgColor: 'bg-low',
    label: 'Low Risk',
    message: 'Fix when convenient',
  },
  SAFE: {
    color: 'text-low',
    bgColor: 'bg-low',
    label: 'Safe',
    message: 'No significant issues found',
  },
};

/**
 * Normalizes a risk level string to uppercase to match RISK_LEVEL_CONFIG keys.
 * Python backend sends lowercase values ("critical", "high", etc.)
 * but TypeScript config uses uppercase keys ("CRITICAL", "HIGH", etc.)
 * 
 * @param riskLevel - The risk level string (case-insensitive)
 * @returns The normalized uppercase risk level, defaults to 'SAFE' if invalid
 */
export function normalizeRiskLevel(riskLevel: string | undefined | null): RiskLevel {
  if (!riskLevel) {
    return 'SAFE';
  }
  
  const normalized = riskLevel.toUpperCase() as RiskLevel;
  
  // Validate that it's a valid risk level
  if (normalized in RISK_LEVEL_CONFIG) {
    return normalized;
  }
  
  // Default to SAFE if invalid
  return 'SAFE';
}
