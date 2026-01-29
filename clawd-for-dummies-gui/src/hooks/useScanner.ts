import { useCallback, useEffect, useRef } from 'react';
import { useScanStore } from '../stores/scanStore';
import { ScanProgress, ScanResult } from '../types/scan';
import { normalizeScanResult } from '../utils/scanResultNormalizer';
import { PRIORITY_FINDING_ID } from '../utils/findingUtils';

// Extend window type for electron bridge
declare global {
  interface Window {
    scanner?: {
      startScan: (modules: string[]) => Promise<ScanResult>;
      cancelScan: () => Promise<boolean>;
      onProgress: (callback: (progress: ScanProgress) => void) => () => void;
      onResult: (callback: (result: ScanResult) => void) => () => void;
    };
  }
}

export function useScanner() {
  const {
    status,
    scanResult,
    progress,
    modules,
    setStatus,
    setScanResult,
    setProgress,
    setError,
    reset,
    getEnabledModules,
  } = useScanStore();

  // Use ref to track if component is mounted (prevents memory leaks from stale callbacks)
  const isMountedRef = useRef(true);

  // Set up IPC listeners with proper cleanup
  useEffect(() => {
    isMountedRef.current = true;
    
    if (!window.scanner) return;

    // Store cleanup functions in local array (not ref) to avoid stale closures
    const cleanups: Array<() => void> = [];

    const unsubProgress = window.scanner.onProgress((progressUpdate) => {
      // Guard against updates after unmount
      if (isMountedRef.current) {
        setProgress(progressUpdate);
      }
    });
    cleanups.push(unsubProgress);

    const unsubResult = window.scanner.onResult((result) => {
      // Guard against updates after unmount
      if (isMountedRef.current) {
        // Normalize the result from Python backend (snake_case to camelCase)
        const normalizedResult = normalizeScanResult(result as unknown as Record<string, unknown>);
        setScanResult(normalizedResult);
      }
    });
    cleanups.push(unsubResult);

    // Cleanup function - called on unmount or deps change
    return () => {
      isMountedRef.current = false;
      cleanups.forEach(cleanup => cleanup());
    };
  }, [setProgress, setScanResult]);

  const startScan = useCallback(async () => {
    if (!window.scanner) {
      // Browser-only mode without Electron - show clear warning
      console.warn('⚠️ Running in DEMO MODE - No Electron bridge detected');
      console.warn('To run real scans, use: npm run electron:dev');

      setStatus('scanning');
      // Simulate progress
      const enabledModules = getEnabledModules();
      for (let i = 0; i < enabledModules.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 500));
        const module = enabledModules[i];
        if (module) {
          setProgress({
            module,
            status: 'complete',
            percentage: ((i + 1) / enabledModules.length) * 100,
          });
        }
      }
      // Set demo result with clear indication this is fake data
      setScanResult(getDemoResult());
      return;
    }

    try {
      setStatus('scanning');
      setError(null);
      const enabledModules = getEnabledModules();
      await window.scanner.startScan(enabledModules);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Scan failed');
    }
  }, [getEnabledModules, setStatus, setProgress, setScanResult, setError]);

  const cancelScan = useCallback(async () => {
    if (window.scanner) {
      await window.scanner.cancelScan();
    }
    setStatus('idle');
    reset();
  }, [setStatus, reset]);

  const isScanning = status === 'scanning';
  const isComplete = status === 'complete';
  const hasResults = scanResult !== null;

  return {
    status,
    scanResult,
    progress,
    modules,
    isScanning,
    isComplete,
    hasResults,
    startScan,
    cancelScan,
  };
}

// Demo data for testing without Electron
// ⚠️ THIS IS FAKE DATA - Real scanning requires Electron mode
function getDemoResult(): ScanResult {
  return {
    scanId: 'demo-001',
    timestamp: new Date().toISOString(),
    durationSeconds: 2.5,
    overallRiskScore: 7.5,
    riskLevel: 'HIGH',
    criticalCount: 1,
    highCount: 2,
    mediumCount: 1,
    lowCount: 1,
    infoCount: 2,
    systemInfo: {
      platform: 'demo',
      platformDisplay: '⚠️ DEMO MODE - Not Real Data',
      pythonVersion: '3.11.0',
      username: 'demo_user',
      isAdmin: false,
      localIps: ['192.168.1.100'],
    },
    findings: [
      // Priority Finding: Moltbot/Clawdbot Not Installed
      // This demonstrates how the GUI displays the "Getting Started" message
      {
        id: PRIORITY_FINDING_ID,
        title: 'Moltbot/Clawdbot Not Installed or Not Configured',
        description: 'No Moltbot or Clawdbot configuration files were found on your system. This likely means Moltbot/Clawdbot is not installed or has not been configured yet. If you intended to scan Moltbot/Clawdbot security, you will need to install it first.',
        severity: 'INFO',
        category: 'CONFIGURATION',
        cvssScore: 0,
        location: 'System configuration',
        remediation: 'Install Moltbot to use the full security scanning capabilities.',
        remediationSteps: [
          { step: 1, instruction: 'Install Node.js (version 22 or higher) from https://nodejs.org/' },
          { step: 2, instruction: 'Install Moltbot globally', code: 'npm install -g moltbot@latest' },
          { step: 3, instruction: 'Run the onboarding wizard', code: 'moltbot onboard --install-daemon' },
          { step: 4, instruction: 'Start the gateway', code: 'moltbot gateway --port 18789' },
          { step: 5, instruction: 'Run this scanner again to check your Moltbot security configuration' },
        ],
        references: [
          'https://docs.molt.bot/start/getting-started',
          'https://docs.molt.bot/install',
          'https://github.com/moltbot/moltbot',
        ],
      },
      {
        id: 'demo-1',
        title: 'Clawdbot Gateway Exposed to Network',
        description: 'Your Clawdbot gateway (port 18789) is accessible from the internet. Anyone can connect to your computer!',
        severity: 'CRITICAL',
        category: 'PORT_EXPOSURE',
        cvssScore: 9.5,
        location: 'Port 18789 bound to 0.0.0.0',
        remediation: 'Configure authentication or bind to 127.0.0.1',
        remediationSteps: [
          { step: 1, instruction: 'Open your Clawdbot configuration file' },
          { step: 2, instruction: 'Find the "bind" setting' },
          { step: 3, instruction: 'Change "0.0.0.0" to "127.0.0.1"', code: '"bind": "127.0.0.1"' },
          { step: 4, instruction: 'Save and restart Moltbot/Clawdbot' },
        ],
        references: ['https://docs.clawdbot.example/security'],
      },
      {
        id: 'demo-2',
        title: 'API Keys Found in Plain Text',
        description: 'Your OpenAI key is visible in configuration files accessible to any program.',
        severity: 'HIGH',
        category: 'CREDENTIALS',
        cvssScore: 8.5,
        location: '~/.moltbot/moltbot.json',
        remediation: 'Move API keys to environment variables',
        remediationSteps: [
          { step: 1, instruction: 'Create a .env file in your home directory' },
          { step: 2, instruction: 'Move the API key to environment variable', code: 'OPENAI_API_KEY=sk-...' },
          { step: 3, instruction: 'Update config to reference environment variable' },
        ],
        references: ['https://platform.openai.com/docs/api-reference'],
      },
      {
        id: 'demo-3',
        title: 'Authentication Bypass Vulnerability',
        description: 'The gateway can be accessed without authentication from localhost.',
        severity: 'HIGH',
        category: 'AUTHENTICATION',
        cvssScore: 8.0,
        location: 'Moltbot/Clawdbot Gateway',
        remediation: 'Enable authentication in Moltbot/Clawdbot configuration',
        remediationSteps: [
          { step: 1, instruction: 'Open your Moltbot/Clawdbot settings' },
          { step: 2, instruction: 'Enable "Require Authentication"' },
          { step: 3, instruction: 'Set a strong password' },
        ],
      },
      {
        id: 'demo-4',
        title: 'Config File World-Readable',
        description: 'Configuration files have overly permissive permissions (644).',
        severity: 'MEDIUM',
        category: 'PERMISSIONS',
        cvssScore: 5.5,
        location: '~/.moltbot/moltbot.json',
        remediation: 'Restrict file permissions to owner only',
        remediationSteps: [
          { step: 1, instruction: 'Run chmod 600 on config files', code: 'chmod 600 ~/.moltbot/moltbot.json' },
        ],
      },
      {
        id: 'demo-5',
        title: 'Backup Files Present',
        description: 'Old backup files found that may contain sensitive data.',
        severity: 'LOW',
        category: 'CONFIGURATION',
        cvssScore: 3.0,
        location: '~/.moltbot/moltbot.json.bak',
        remediation: 'Remove unnecessary backup files',
        remediationSteps: [
          { step: 1, instruction: 'Delete backup files securely' },
        ],
      },
      {
        id: 'demo-6',
        title: 'Moltbot/Clawdbot Running',
        description: 'Moltbot/Clawdbot process is currently running on this system.',
        severity: 'INFO',
        category: 'CONFIGURATION',
        cvssScore: 0,
        location: 'Process ID: 12345',
        remediation: 'No action required - informational only',
        remediationSteps: [],
      },
    ],
  };
}
