import { useState, useCallback } from 'react';

export type ExportFormat = 'html' | 'json' | 'markdown';

interface ExportOptions {
  includeSystemInfo: boolean;
  includeRemediation: boolean;
  includeTechnicalDetails: boolean;
  filename?: string;
}

declare global {
  interface Window {
    exporter?: {
      generate: (format: ExportFormat, options: ExportOptions) => Promise<string>;
    };
  }
}

export function useExport() {
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const exportReport = useCallback(async (format: ExportFormat, options: ExportOptions) => {
    setIsExporting(true);
    setExportError(null);

    try {
      if (window.exporter) {
        const filePath = await window.exporter.generate(format, options);
        return filePath;
      } else {
        // Demo mode - create downloadable content
        const content = getDemoExportContent(format);
        const blob = new Blob([content], { type: getContentType(format) });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = options.filename || `security_report.${format}`;
        a.click();
        URL.revokeObjectURL(url);
        return options.filename || `security_report.${format}`;
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Export failed';
      setExportError(message);
      throw error;
    } finally {
      setIsExporting(false);
    }
  }, []);

  return { exportReport, isExporting, exportError };
}

function getContentType(format: ExportFormat): string {
  switch (format) {
    case 'html':
      return 'text/html';
    case 'json':
      return 'application/json';
    case 'markdown':
      return 'text/markdown';
    default:
      return 'text/plain';
  }
}

function getDemoExportContent(format: ExportFormat): string {
  const timestamp = new Date().toISOString();
  
  if (format === 'json') {
    return JSON.stringify({
      exportTime: timestamp,
      message: 'Demo export - run with Electron for full functionality',
    }, null, 2);
  }
  
  if (format === 'markdown') {
    return `# Security Scan Report\n\nGenerated: ${timestamp}\n\n*Demo export - run with Electron for full functionality*`;
  }
  
  return `<!DOCTYPE html>
<html>
<head><title>Security Report</title></head>
<body>
<h1>Security Scan Report</h1>
<p>Generated: ${timestamp}</p>
<p><em>Demo export - run with Electron for full functionality</em></p>
</body>
</html>`;
}
