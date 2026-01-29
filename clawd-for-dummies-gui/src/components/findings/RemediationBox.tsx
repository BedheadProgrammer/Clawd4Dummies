import { memo, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Wrench, Copy, Check, FolderOpen, HelpCircle } from 'lucide-react';
import { RemediationStep } from '../../types/finding';
import { useClipboard } from '../../hooks/useClipboard';

interface RemediationBoxProps {
  steps: readonly RemediationStep[];
  remediation: string;
}

export const RemediationBox = memo(function RemediationBox({
  steps,
  remediation,
}: RemediationBoxProps) {
  const { copy, copied } = useClipboard();

  // Format steps for copying
  const stepsText = useMemo(() => {
    return steps
      .map((step) => {
        let text = `${step.step}. ${step.instruction}`;
        if (step.code) {
          text += `\n   ${step.code}`;
        }
        return text;
      })
      .join('\n');
  }, [steps]);

  const handleCopy = () => {
    copy(stepsText);
  };

  const handleOpenLocation = (filePath?: string) => {
    if (filePath) {
      // In Electron, this would open the file location
      console.log('Open location:', filePath);
    }
  };

  return (
    <div className="bg-space-black/50 rounded-lg border border-text-secondary/20 overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 bg-space-black/30 border-b border-text-secondary/10">
        <Wrench className="w-4 h-4 text-action-blue" />
        <span className="font-semibold text-text-primary">How to Fix</span>
      </div>

      {/* Summary */}
      <div className="px-4 py-3 border-b border-text-secondary/10">
        <p className="text-sm text-text-secondary">{remediation}</p>
      </div>

      {/* Steps */}
      <div className="px-4 py-4">
        <ol className="space-y-3">
          {steps.map((step) => (
            <motion.li
              key={step.step}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: step.step * 0.1 }}
              className="flex gap-3"
            >
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-action-blue/20 text-action-blue text-sm flex items-center justify-center font-medium">
                {step.step}
              </span>
              <div className="flex-1">
                <p className="text-text-primary text-sm">{step.instruction}</p>
                {step.code && (
                  <code className="block mt-2 px-3 py-2 bg-space-black rounded text-xs font-mono text-action-blue border border-text-secondary/20">
                    {step.code}
                  </code>
                )}
                {step.filePath && (
                  <button
                    onClick={() => handleOpenLocation(step.filePath)}
                    className="mt-2 flex items-center gap-1 text-xs text-action-blue hover:underline"
                  >
                    <FolderOpen className="w-3 h-3" />
                    <span className="font-mono">{step.filePath}</span>
                  </button>
                )}
              </div>
            </motion.li>
          ))}
        </ol>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 px-4 py-3 bg-space-black/30 border-t border-text-secondary/10">
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-elevated transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-low" />
              <span className="text-low">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span>Copy Steps</span>
            </>
          )}
        </button>
        <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-elevated transition-colors">
          <HelpCircle className="w-4 h-4" />
          <span>Help</span>
        </button>
      </div>
    </div>
  );
});
