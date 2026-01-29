import { memo, useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, MapPin, ExternalLink, Copy, Check, Bot } from 'lucide-react';
import { Card } from '../common/Card';
import { SeverityBadge } from './SeverityBadge';
import { RemediationBox } from './RemediationBox';
import { Finding, SEVERITY_CONFIG } from '../../types/finding';
import { useScanStore } from '../../stores/scanStore';

interface FindingCardProps {
  finding: Finding;
}

export const FindingCard = memo(function FindingCard({ finding }: FindingCardProps) {
  const { expandedFindings, toggleFinding } = useScanStore();
  const isExpanded = expandedFindings.has(finding.id);
  const config = SEVERITY_CONFIG[finding.severity];
  const [copied, setCopied] = useState(false);

  const handleToggle = useCallback(() => {
    toggleFinding(finding.id);
  }, [finding.id, toggleFinding]);

  const handleCopyPrompt = useCallback(async () => {
    if (finding.fixPrompt) {
      try {
        await navigator.clipboard.writeText(finding.fixPrompt);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = finding.fixPrompt;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    }
  }, [finding.fixPrompt]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        padding="none"
        borderColor={config.borderColor}
        className={`overflow-hidden transition-all ${
          isExpanded ? 'shadow-lg' : 'hover:shadow-md'
        }`}
      >
        {/* Header - Always Visible */}
        <button
          onClick={handleToggle}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-space-black/30 transition-colors"
        >
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <ChevronDown
              className={`w-5 h-5 text-text-secondary transition-transform flex-shrink-0 ${
                isExpanded ? 'rotate-180' : ''
              }`}
            />
            <span className={`font-semibold truncate ${config.color}`}>
              {finding.title}
            </span>
          </div>
          <SeverityBadge severity={finding.severity} score={finding.cvssScore} />
        </button>

        {/* Expanded Content */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.25 }}
            >
              <div className="px-4 pb-4 pt-0 border-t border-text-secondary/10">
                {/* Description */}
                <p className="text-text-primary mt-4 mb-4">
                  {finding.description}
                </p>

                {/* Location */}
                {finding.location && (
                  <div className="flex items-center gap-2 text-sm text-text-secondary mb-4">
                    <MapPin className="w-4 h-4" />
                    <span className="font-mono text-xs">{finding.location}</span>
                  </div>
                )}

                {/* Remediation Steps */}
                {finding.remediationSteps.length > 0 && (
                  <RemediationBox
                    steps={finding.remediationSteps}
                    remediation={finding.remediation}
                  />
                )}

                {/* AI Fix Prompt */}
                {finding.fixPrompt && (
                  <div className="mt-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Bot className="w-4 h-4 text-action-blue" aria-hidden="true" />
                        <p className="text-sm font-medium text-text-primary" id={`fix-prompt-label-${finding.id}`}>AI Fix Prompt</p>
                      </div>
                      <button
                        onClick={handleCopyPrompt}
                        className="flex items-center gap-1 px-2 py-1 text-xs bg-space-black/50 hover:bg-space-black/70 rounded transition-colors"
                        aria-label={copied ? "Copied to clipboard" : "Copy AI fix prompt to clipboard"}
                        aria-live="polite"
                      >
                        {copied ? (
                          <>
                            <Check className="w-3 h-3 text-green-400" aria-hidden="true" />
                            <span className="text-green-400">Copied!</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3 text-text-secondary" aria-hidden="true" />
                            <span className="text-text-secondary">Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                    <div
                      className="bg-space-black/70 rounded-lg p-3 font-mono text-xs text-text-secondary leading-relaxed whitespace-pre-wrap"
                      role="region"
                      aria-labelledby={`fix-prompt-label-${finding.id}`}
                    >
                      {finding.fixPrompt}
                    </div>
                  </div>
                )}

                {/* Reference Links */}
                {finding.references && finding.references.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm text-text-secondary mb-2">Learn More:</p>
                    <div className="flex flex-wrap gap-2">
                      {finding.references.map((link, index) => {
                        // TYPE SAFETY: Safely parse URL with error handling
                        let hostname: string;
                        try {
                          hostname = new URL(link).hostname;
                        } catch {
                          // Fallback for invalid URLs
                          hostname = link.length > 30 ? `${link.slice(0, 30)}...` : link;
                        }
                        return (
                          <a
                            key={index}
                            href={link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-sm text-action-blue hover:underline"
                          >
                            <ExternalLink className="w-3 h-3" />
                            {hostname}
                          </a>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
});
