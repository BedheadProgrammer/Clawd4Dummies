import { memo } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, ExternalLink, Copy, Check } from 'lucide-react';
import { Finding } from '../../../types/finding';
import { useState, useCallback } from 'react';

interface PriorityAlertProps {
  finding: Finding;
  className?: string;
}

export const PriorityAlert = memo(function PriorityAlert({ finding, className = '' }: PriorityAlertProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleCopy = useCallback(async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: -10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className={`relative overflow-hidden rounded-xl ${className}`}
      role="alert"
      aria-live="assertive"
    >
      {/* Pulsing glow effect */}
      <motion.div
        className="absolute inset-0 rounded-xl"
        animate={{
          boxShadow: [
            '0 0 20px rgba(248, 81, 73, 0.3), inset 0 0 20px rgba(248, 81, 73, 0.1)',
            '0 0 40px rgba(248, 81, 73, 0.5), inset 0 0 30px rgba(248, 81, 73, 0.15)',
            '0 0 20px rgba(248, 81, 73, 0.3), inset 0 0 20px rgba(248, 81, 73, 0.1)',
          ],
        }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Main container */}
      <div className="relative bg-gradient-to-r from-red-800 via-red-700 to-red-800 border-4 border-red-400 rounded-xl p-6">
        {/* Animated diagonal stripes for extra attention */}
        <div className="absolute inset-0 opacity-[0.08] pointer-events-none overflow-hidden rounded-lg">
          <motion.div
            className="absolute inset-0"
            style={{
              backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.3) 10px, rgba(255,255,255,0.3) 20px)',
              backgroundSize: '200% 200%',
            }}
            animate={{
              backgroundPosition: ['0% 0%', '100% 100%'],
            }}
            transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          />
        </div>

        {/* Content */}
        <div className="relative z-10">
          {/* Header with icon */}
          <div className="flex items-start gap-4">
            <motion.div
              animate={{
                scale: [1, 1.1, 1],
              }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <AlertTriangle className="w-12 h-12 text-white drop-shadow-lg flex-shrink-0" />
            </motion.div>

            <div className="flex-1 min-w-0">
              <h3 className="text-2xl font-display font-bold text-white mb-2 drop-shadow-md">
                {finding.title}
              </h3>
              <p className="text-red-100 text-lg leading-relaxed">
                {finding.description}
              </p>
            </div>
          </div>

          {/* Remediation Steps */}
          {finding.remediationSteps && finding.remediationSteps.length > 0 && (
            <div className="mt-6 bg-black/30 rounded-lg p-5 backdrop-blur-sm">
              <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
                <span className="text-lg">Quick Setup Guide:</span>
              </h4>
              <ol className="space-y-3">
                {finding.remediationSteps.map((step, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                      {step.step}
                    </span>
                    <div className="flex-1">
                      <span className="text-white">{step.instruction}</span>
                      {step.code && (
                        <div className="mt-2 flex items-center gap-2">
                          <code className="bg-black/40 text-red-200 px-3 py-1.5 rounded font-mono text-sm">
                            {step.code}
                          </code>
                          <button
                            onClick={() => handleCopy(step.code!, index)}
                            className="p-1.5 rounded bg-white/10 hover:bg-white/20 transition-colors"
                            aria-label={`Copy command: ${step.code}`}
                          >
                            {copiedIndex === index ? (
                              <Check className="w-4 h-4 text-green-400" />
                            ) : (
                              <Copy className="w-4 h-4 text-white" />
                            )}
                          </button>
                        </div>
                      )}
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Reference Links */}
          {finding.references && finding.references.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-3">
              {finding.references.map((link, index) => (
                <a
                  key={index}
                  href={link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-sm text-red-200 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition-colors"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  Learn More
                </a>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
});
