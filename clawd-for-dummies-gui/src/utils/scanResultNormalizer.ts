import { ScanResult, RiskLevel, SystemInfo } from '../types/scan';
import { Finding, Category, Severity } from '../types/finding';

/**
 * Raw scan result from Python backend (uses snake_case keys)
 */
interface RawScanResult {
  scan_id?: string;
  timestamp?: string;
  duration_seconds?: number;
  findings?: RawFinding[];
  system_info?: RawSystemInfo;
  overall_risk_score?: number;
  risk_level?: string;
  summary?: {
    critical_count?: number;
    high_count?: number;
    medium_count?: number;
    low_count?: number;
    info_count?: number;
  };
  // Also support camelCase keys (from demo mode)
  scanId?: string;
  durationSeconds?: number;
  systemInfo?: SystemInfo;
  overallRiskScore?: number;
  riskLevel?: string;
  criticalCount?: number;
  highCount?: number;
  mediumCount?: number;
  lowCount?: number;
  infoCount?: number;
}

interface RawSystemInfo {
  platform?: string;
  platform_display?: string;
  python_version?: string;
  username?: string;
  is_admin?: boolean;
  local_ips?: string[];
  // Also support camelCase
  platformDisplay?: string;
  pythonVersion?: string;
  isAdmin?: boolean;
  localIps?: string[];
}

interface RawFinding {
  id?: string;
  title?: string;
  description?: string;
  severity?: string;
  category?: string;
  cvss_score?: number;
  location?: string;
  remediation?: string;
  // Support both string arrays (from Python) and object arrays (from demo)
  remediation_steps?: (string | RawRemediationStep)[];
  references?: string[];
  reference_links?: string[];
  // Also support camelCase
  cvssScore?: number;
  remediationSteps?: (string | RawRemediationStep)[];
}

interface RawRemediationStep {
  step?: number;
  instruction?: string;
  code?: string;
  file_path?: string;
  filePath?: string;
}

/**
 * Normalizes remediation steps which can be either:
 * - A list of strings (from Python backend: ["Step 1", "Step 2"])
 * - A list of objects (from demo/other sources: [{step: 1, instruction: "Step 1"}])
 */
function normalizeRemediationSteps(rawSteps: unknown[]): { step: number; instruction: string; code?: string; filePath?: string }[] {
  if (!Array.isArray(rawSteps)) return [];
  
  return rawSteps.map((s, index) => {
    // Handle string steps (from Python backend)
    if (typeof s === 'string') {
      // Check if the string contains a colon indicating a command
      // e.g., "Run: npm install -g moltbot@latest"
      // We limit the search to the first 50 characters to avoid matching colons
      // that appear in URLs or longer explanatory text
      const colonIndex = s.indexOf(': ');
      if (colonIndex > -1 && colonIndex < 50) {
        const instruction = s.substring(0, colonIndex);
        const code = s.substring(colonIndex + 2).trim();
        return {
          step: index + 1,
          instruction,
          code: code.length > 0 ? code : undefined,
        };
      }
      return {
        step: index + 1,
        instruction: s,
      };
    }
    
    // Handle object steps (from demo mode or structured data)
    const rawStep = s as RawRemediationStep;
    return {
      step: rawStep.step ?? index + 1,
      instruction: rawStep.instruction ?? '',
      code: rawStep.code,
      filePath: rawStep.file_path ?? rawStep.filePath,
    };
  });
}

/**
 * Normalizes a raw scan result from the Python backend to the expected TypeScript format.
 * Handles both snake_case (from Python) and camelCase (from demo mode) keys.
 * 
 * @param raw - The raw scan result from the backend
 * @returns A properly formatted ScanResult
 */
export function normalizeScanResult(raw: RawScanResult): ScanResult {
  // Handle both snake_case and camelCase for backward compatibility
  const systemInfo: SystemInfo = {
    platform: raw.system_info?.platform ?? raw.systemInfo?.platform ?? 'unknown',
    platformDisplay: raw.system_info?.platform_display ?? raw.system_info?.platformDisplay ?? raw.systemInfo?.platformDisplay ?? 'Unknown Platform',
    pythonVersion: raw.system_info?.python_version ?? raw.system_info?.pythonVersion ?? raw.systemInfo?.pythonVersion ?? 'N/A',
    username: raw.system_info?.username ?? raw.systemInfo?.username ?? 'unknown',
    isAdmin: raw.system_info?.is_admin ?? raw.system_info?.isAdmin ?? raw.systemInfo?.isAdmin ?? false,
    localIps: raw.system_info?.local_ips ?? raw.system_info?.localIps ?? raw.systemInfo?.localIps ?? [],
  };

  const findings: Finding[] = (raw.findings ?? []).map((f: RawFinding) => ({
    id: f.id ?? 'unknown',
    title: f.title ?? 'Unknown Finding',
    description: f.description ?? '',
    severity: normalizeSeverity(f.severity),
    category: normalizeCategory(f.category),
    cvssScore: f.cvss_score ?? f.cvssScore ?? 0,
    location: f.location,
    remediation: f.remediation ?? '',
    remediationSteps: normalizeRemediationSteps(f.remediation_steps ?? f.remediationSteps ?? []),
    references: f.references ?? f.reference_links ?? [],
  }));

  // Get counts from summary (snake_case from Python) or direct properties (camelCase from demo)
  const criticalCount = raw.summary?.critical_count ?? raw.criticalCount ?? 0;
  const highCount = raw.summary?.high_count ?? raw.highCount ?? 0;
  const mediumCount = raw.summary?.medium_count ?? raw.mediumCount ?? 0;
  const lowCount = raw.summary?.low_count ?? raw.lowCount ?? 0;
  const infoCount = raw.summary?.info_count ?? raw.infoCount ?? 0;

  return {
    scanId: raw.scan_id ?? raw.scanId ?? 'unknown',
    timestamp: raw.timestamp ?? new Date().toISOString(),
    durationSeconds: raw.duration_seconds ?? raw.durationSeconds ?? 0,
    findings,
    systemInfo,
    overallRiskScore: raw.overall_risk_score ?? raw.overallRiskScore ?? 0,
    riskLevel: normalizeRiskLevelString(raw.risk_level ?? raw.riskLevel ?? 'safe'),
    criticalCount,
    highCount,
    mediumCount,
    lowCount,
    infoCount,
  };
}

/**
 * Normalizes a risk level string to uppercase RiskLevel type
 */
function normalizeRiskLevelString(level: string): RiskLevel {
  const normalized = level.toUpperCase();
  if (['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'SAFE'].includes(normalized)) {
    return normalized as RiskLevel;
  }
  return 'SAFE';
}

/**
 * Normalizes severity string to Severity type
 */
function normalizeSeverity(severity: string | undefined): Severity {
  if (!severity) return 'INFO';
  const normalized = severity.toUpperCase();
  if (['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'].includes(normalized)) {
    return normalized as Severity;
  }
  return 'INFO';
}

/**
 * Normalizes category string to Category type
 */
function normalizeCategory(category: string | undefined): Category {
  if (!category) return 'CONFIGURATION';
  const normalized = category.toUpperCase();
  const validCategories = ['PORT_EXPOSURE', 'AUTHENTICATION', 'CREDENTIALS', 'CONFIGURATION', 'PERMISSIONS', 'NETWORK'];
  if (validCategories.includes(normalized)) {
    return normalized as Category;
  }
  return 'CONFIGURATION';
}
