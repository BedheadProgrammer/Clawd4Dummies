import { memo, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield,
  AlertTriangle,
  AlertCircle,
  Info,
  Lightbulb,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  ExternalLink,
  Wrench
} from 'lucide-react';
import { Finding, Severity, Category } from '../../../types/finding';
import { SeverityPill } from './SeverityPill';
import { USER_FRIENDLY_SEVERITY } from '../../../utils/findingUtils';

interface FindingTileProps {
  finding: Finding;
}

// Icon mapping for severity
const SEVERITY_ICONS: Record<Severity, typeof AlertTriangle> = {
  CRITICAL: AlertTriangle,
  HIGH: AlertCircle,
  MEDIUM: Info,
  LOW: Lightbulb,
  INFO: Info,
};

// Icon mapping for categories
const CATEGORY_ICONS: Record<Category, typeof Shield> = {
  PORT_EXPOSURE: Shield,
  AUTHENTICATION: Shield,
  CREDENTIALS: Shield,
  CONFIGURATION: Wrench,
  PERMISSIONS: Shield,
  NETWORK: Shield,
};

export const FindingTile = memo(function FindingTile({ finding }: FindingTileProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const severityConfig = USER_FRIENDLY_SEVERITY[finding.severity];
  const SeverityIcon = SEVERITY_ICONS[finding.severity];
  const CategoryIcon = CATEGORY_ICONS[finding.category] || Shield;

  const handleCopy = useCallback(async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, []);

  const toggleExpanded = useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        rounded-2xl overflow-hidden transition-all duration-300
        bg-elevated border ${severityConfig.borderColor}
        hover:shadow-lg hover:shadow-black/20
      `}
    >
      {/* Main Card Content */}
      <div className="p-5">
        {/* Header Row */}
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className={`
            flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center
            ${severityConfig.bgColor}
          `}>
            <SeverityIcon className={`w-6 h-6 ${severityConfig.textColor}`} />
          </div>

          {/* Title and Description */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-3 mb-2">
              <h3 className="text-lg font-semibold text-text-primary leading-tight">
                {finding.title}
              </h3>
              <SeverityPill severity={finding.severity} />
            </div>

            <p className="text-text-secondary text-sm leading-relaxed line-clamp-2">
              {finding.description}
            </p>
          </div>
        </div>

        {/* Action Button */}
        <div className="mt-4 flex items-center justify-between">
          <button
            onClick={toggleExpanded}
            className={`
              inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
              transition-all duration-200
              ${severityConfig.bgColor} ${severityConfig.textColor}
              hover:brightness-110 active:scale-[0.98]
            `}
          >
            {isExpanded ? (
              <>
                <ChevronUp className="w-4 h-4" />
                Hide Steps
              </>
            ) : (
              <>
                <Wrench className="w-4 h-4" />
                How to Fix
              </>
            )}
          </button>

          {finding.location && (
            <span className="text-xs text-text-secondary bg-space-black/50 px-3 py-1.5 rounded-lg">
              {finding.location}
            </span>
          )}
        </div>
      </div>

      {/* Expanded Remediation Section */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 pt-0">
              <div className="bg-space-black/50 rounded-xl p-5">
                {/* Why This Matters */}
                <div className="mb-5">
                  <h4 className="text-sm font-semibold text-text-primary mb-2 flex items-center gap-2">
                    <Info className="w-4 h-4 text-action-blue" />
                    Why This Matters
                  </h4>
                  <p className="text-text-secondary text-sm">
                    {finding.remediation || finding.description}
                  </p>
                </div>

                {/* Steps to Fix */}
                {finding.remediationSteps && finding.remediationSteps.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
                      <Wrench className="w-4 h-4 text-low" />
                      Steps to Fix
                    </h4>
                    <ol className="space-y-3">
                      {finding.remediationSteps.map((step, index) => (
                        <li key={index} className="flex items-start gap-3">
                          <span className={`
                            flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center
                            text-xs font-bold ${severityConfig.bgColor} ${severityConfig.textColor}
                          `}>
                            {step.step}
                          </span>
                          <div className="flex-1 pt-0.5">
                            <p className="text-text-primary text-sm">{step.instruction}</p>
                            {step.code && (
                              <div className="mt-2 flex items-center gap-2">
                                <code className="flex-1 bg-black/50 text-action-blue px-3 py-2 rounded-lg text-xs font-mono overflow-x-auto">
                                  {step.code}
                                </code>
                                <button
                                  onClick={() => handleCopy(step.code!, index)}
                                  className="flex-shrink-0 p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                                  aria-label={`Copy command`}
                                >
                                  {copiedIndex === index ? (
                                    <Check className="w-4 h-4 text-low" />
                                  ) : (
                                    <Copy className="w-4 h-4 text-text-secondary" />
                                  )}
                                </button>
                              </div>
                            )}
                            {step.filePath && (
                              <p className="mt-1 text-xs text-text-secondary">
                                File: <span className="text-action-blue">{step.filePath}</span>
                              </p>
                            )}
                          </div>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}

                {/* Learn More Links */}
                {finding.references && finding.references.length > 0 && (
                  <div className="mt-5 pt-4 border-t border-text-secondary/10">
                    <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                      Learn More
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {finding.references.map((link, index) => (
                        <a
                          key={index}
                          href={link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 text-xs text-action-blue hover:text-action-blue/80 bg-action-blue/10 hover:bg-action-blue/20 px-3 py-1.5 rounded-lg transition-colors"
                        >
                          <ExternalLink className="w-3 h-3" />
                          Resource {index + 1}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});
