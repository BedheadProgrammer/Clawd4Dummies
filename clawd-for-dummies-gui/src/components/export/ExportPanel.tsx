import { memo, useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, FileJson, FileCode, Printer, Download, Check } from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { useExport, ExportFormat } from '../../hooks/useExport';
import { useScanStore } from '../../stores/scanStore';

interface FormatOption {
  format: ExportFormat;
  icon: React.ReactNode;
  label: string;
  description: string;
}

const formatOptions: FormatOption[] = [
  {
    format: 'html',
    icon: <FileText className="w-6 h-6" />,
    label: 'HTML',
    description: 'Visual Report',
  },
  {
    format: 'json',
    icon: <FileJson className="w-6 h-6" />,
    label: 'JSON',
    description: 'Machine Readable',
  },
  {
    format: 'markdown',
    icon: <FileCode className="w-6 h-6" />,
    label: 'Markdown',
    description: 'Shareable (GitHub)',
  },
];

export const ExportPanel = memo(function ExportPanel() {
  const { status, scanResult } = useScanStore();
  const { exportReport, isExporting, exportError } = useExport();
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('html');
  const [includeSystemInfo, setIncludeSystemInfo] = useState(true);
  const [includeRemediation, setIncludeRemediation] = useState(true);
  const [includeTechnicalDetails, setIncludeTechnicalDetails] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  
  // MEMORY LEAK FIX: Track timeout for cleanup
  const successTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // MEMORY LEAK FIX: Clear timeout on unmount
  useEffect(() => {
    return () => {
      if (successTimeoutRef.current) {
        clearTimeout(successTimeoutRef.current);
      }
    };
  }, []);

  // Don't show if no results
  if (status !== 'complete' || !scanResult) return null;

  const handleExport = async () => {
    try {
      const date = new Date().toISOString().split('T')[0];
      const filename = `clawd_security_report_${date}.${selectedFormat}`;
      
      await exportReport(selectedFormat, {
        includeSystemInfo,
        includeRemediation,
        includeTechnicalDetails,
        filename,
      });
      
      setExportSuccess(true);
      
      // Clear any existing timeout before setting a new one
      if (successTimeoutRef.current) {
        clearTimeout(successTimeoutRef.current);
      }
      successTimeoutRef.current = setTimeout(() => {
        setExportSuccess(false);
        successTimeoutRef.current = null;
      }, 3000);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  return (
    <motion.div
      id="export-section"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mt-6"
    >
      <Card>
        <h3 className="text-lg font-display font-semibold text-text-primary mb-6 flex items-center gap-2">
          <Download className="w-5 h-5 text-action-blue" />
          Export Report
        </h3>

        {/* Format Selection */}
        <div className="mb-6">
          <p className="text-sm text-text-secondary mb-3">Choose Format:</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {formatOptions.map((option) => (
              <button
                key={option.format}
                onClick={() => setSelectedFormat(option.format)}
                className={`flex flex-col items-center p-4 rounded-lg border-2 transition-all ${
                  selectedFormat === option.format
                    ? 'border-action-blue bg-action-blue/10'
                    : 'border-text-secondary/30 hover:border-text-secondary/50'
                }`}
              >
                <span className={selectedFormat === option.format ? 'text-action-blue' : 'text-text-secondary'}>
                  {option.icon}
                </span>
                <span className="font-medium text-text-primary mt-2">{option.label}</span>
                <span className="text-xs text-text-secondary">{option.description}</span>
              </button>
            ))}
            {/* Print Option */}
            <button
              onClick={() => window.print()}
              className="flex flex-col items-center p-4 rounded-lg border-2 border-text-secondary/30 hover:border-text-secondary/50 transition-all"
            >
              <Printer className="w-6 h-6 text-text-secondary" />
              <span className="font-medium text-text-primary mt-2">Print</span>
              <span className="text-xs text-text-secondary">Paper Report</span>
            </button>
          </div>
        </div>

        {/* Options */}
        <div className="mb-6 space-y-3">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={includeSystemInfo}
              onChange={(e) => setIncludeSystemInfo(e.target.checked)}
              className="w-4 h-4 rounded border-text-secondary bg-space-black text-action-blue focus:ring-action-blue"
            />
            <span className="text-text-primary text-sm">Include System Information</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={includeRemediation}
              onChange={(e) => setIncludeRemediation(e.target.checked)}
              className="w-4 h-4 rounded border-text-secondary bg-space-black text-action-blue focus:ring-action-blue"
            />
            <span className="text-text-primary text-sm">Include Remediation Steps</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={includeTechnicalDetails}
              onChange={(e) => setIncludeTechnicalDetails(e.target.checked)}
              className="w-4 h-4 rounded border-text-secondary bg-space-black text-action-blue focus:ring-action-blue"
            />
            <span className="text-text-primary text-sm">Include Technical Details (Advanced)</span>
          </label>
        </div>

        {/* Filename Preview */}
        <div className="mb-6 p-3 bg-space-black/50 rounded-lg">
          <p className="text-xs text-text-secondary mb-1">Filename:</p>
          <p className="font-mono text-sm text-text-primary">
            clawd_security_report_{new Date().toISOString().split('T')[0]}.{selectedFormat}
          </p>
        </div>

        {/* Export Error */}
        {exportError && (
          <div className="mb-4 p-3 bg-critical/10 border border-critical rounded-lg text-critical text-sm">
            {exportError}
          </div>
        )}

        {/* Export Button */}
        <div className="flex justify-center">
          <Button
            size="lg"
            onClick={handleExport}
            disabled={isExporting}
            isLoading={isExporting}
            leftIcon={exportSuccess ? <Check className="w-5 h-5" /> : <Download className="w-5 h-5" />}
            className={exportSuccess ? 'bg-low hover:bg-low' : ''}
          >
            {exportSuccess ? 'Downloaded!' : 'Download Report'}
          </Button>
        </div>
      </Card>
    </motion.div>
  );
});
