import { memo, useState, useCallback, useEffect } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import {
  AlertTriangle,
  Copy,
  Check,
  ExternalLink,
  ChevronDown,
  Zap,
  Terminal
} from 'lucide-react';
import { Finding } from '../../../types/finding';

interface PriorityInstallAlertProps {
  finding: Finding;
  className?: string;
  hasMoreFindings?: boolean; // Whether there are more findings below
}

// Animation variants for staggered children
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: 'easeOut' },
  },
};

// Floating particle component
const FloatingParticle = memo(function FloatingParticle({
  delay,
  duration,
  startX,
  startY,
  prefersReducedMotion,
}: {
  delay: number;
  duration: number;
  startX: string;
  startY: string;
  prefersReducedMotion: boolean;
}) {
  // Don't render particles if reduced motion is preferred
  if (prefersReducedMotion) return null;
  
  return (
    <motion.div
      className="absolute w-1 h-1 rounded-full bg-amber-400/60"
      style={{ left: startX, top: startY }}
      animate={{
        y: [0, -30, 0],
        x: [0, 10, -10, 0],
        opacity: [0.3, 0.8, 0.3],
        scale: [1, 1.5, 1],
      }}
      transition={{
        duration,
        delay,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    />
  );
});

// Corner bracket component for targeting effect
const CornerBracket = memo(function CornerBracket({
  position,
  prefersReducedMotion,
}: {
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  prefersReducedMotion: boolean;
}) {
  const positionClasses = {
    'top-left': 'top-2 left-2 border-t-2 border-l-2',
    'top-right': 'top-2 right-2 border-t-2 border-r-2',
    'bottom-left': 'bottom-2 left-2 border-b-2 border-l-2',
    'bottom-right': 'bottom-2 right-2 border-b-2 border-r-2',
  };

  return (
    <motion.div
      className={`absolute w-6 h-6 border-amber-400/70 ${positionClasses[position]}`}
      animate={prefersReducedMotion ? {} : {
        opacity: [0.5, 1, 0.5],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    />
  );
});

export const PriorityInstallAlert = memo(function PriorityInstallAlert({
  finding,
  className = '',
  hasMoreFindings = true,
}: PriorityInstallAlertProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const prefersReducedMotion = useReducedMotion() ?? false;

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
      initial={{ opacity: 0, scale: 0.95, y: -20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: prefersReducedMotion ? 0.1 : 0.6, ease: [0.23, 1, 0.32, 1] }}
      className={`relative overflow-hidden rounded-2xl ${className}`}
      role="alert"
      aria-live="assertive"
    >
      {/* Animated border glow effect - disabled if reduced motion preferred */}
      {!prefersReducedMotion && (
        <motion.div
          className="absolute inset-0 rounded-2xl"
          animate={{
            boxShadow: [
              '0 0 20px rgba(245, 158, 11, 0.4), inset 0 0 20px rgba(245, 158, 11, 0.1)',
              '0 0 50px rgba(249, 115, 22, 0.6), inset 0 0 40px rgba(249, 115, 22, 0.15)',
              '0 0 20px rgba(245, 158, 11, 0.4), inset 0 0 20px rgba(245, 158, 11, 0.1)',
            ],
          }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        />
      )}

      {/* Main container with gradient */}
      <div className="relative bg-gradient-to-br from-amber-600 via-orange-600 to-red-600 rounded-2xl p-1">
        <div className="relative bg-gradient-to-br from-amber-900/95 via-orange-900/95 to-red-900/95 rounded-xl overflow-hidden">
          {/* Scanning line effect - disabled if reduced motion preferred */}
          {!prefersReducedMotion && (
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <motion.div
                className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-amber-400/80 to-transparent"
                animate={{
                  y: [0, 300, 0],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: 'linear',
                }}
              />
            </div>
          )}

          {/* Floating particles - reduced count for better performance (4 instead of 7) */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <FloatingParticle delay={0} duration={4} startX="10%" startY="20%" prefersReducedMotion={prefersReducedMotion} />
            <FloatingParticle delay={0.7} duration={3.5} startX="85%" startY="35%" prefersReducedMotion={prefersReducedMotion} />
            <FloatingParticle delay={1.4} duration={4.5} startX="25%" startY="70%" prefersReducedMotion={prefersReducedMotion} />
            <FloatingParticle delay={2.1} duration={3.8} startX="70%" startY="55%" prefersReducedMotion={prefersReducedMotion} />
          </div>

          {/* Corner brackets for targeting effect */}
          <CornerBracket position="top-left" prefersReducedMotion={prefersReducedMotion} />
          <CornerBracket position="top-right" prefersReducedMotion={prefersReducedMotion} />
          <CornerBracket position="bottom-left" prefersReducedMotion={prefersReducedMotion} />
          <CornerBracket position="bottom-right" prefersReducedMotion={prefersReducedMotion} />

          {/* Content container */}
          <motion.div
            className="relative z-10 p-6 sm:p-8"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {/* Header Section */}
            <motion.div variants={itemVariants} className="flex items-start gap-4 mb-6">
              {/* Animated Warning Icon */}
              <motion.div
                className="flex-shrink-0"
                animate={prefersReducedMotion ? {} : {
                  scale: [1, 1.15, 1],
                  rotate: [0, -5, 5, 0],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              >
                <div className="relative">
                  <AlertTriangle className="w-14 h-14 text-amber-300 drop-shadow-lg" />
                  {!prefersReducedMotion && (
                    <motion.div
                      className="absolute inset-0 flex items-center justify-center"
                      animate={{ opacity: [0, 0.5, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      <AlertTriangle className="w-14 h-14 text-white" />
                    </motion.div>
                  )}
                </div>
              </motion.div>

              <div className="flex-1 min-w-0">
                {/* ACTION REQUIRED Badge */}
                <motion.div
                  className="inline-flex items-center gap-2 px-3 py-1 bg-amber-500/30 border border-amber-400/50 rounded-full mb-3"
                  animate={prefersReducedMotion ? {} : {
                    backgroundColor: ['rgba(245, 158, 11, 0.3)', 'rgba(249, 115, 22, 0.4)', 'rgba(245, 158, 11, 0.3)'],
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Zap className="w-4 h-4 text-amber-300" />
                  <span className="text-xs font-bold uppercase tracking-wider text-amber-200">
                    Action Required
                  </span>
                </motion.div>

                {/* Finding Title */}
                <h3 className="text-2xl sm:text-3xl font-display font-bold text-white mb-3 leading-tight drop-shadow-md">
                  {finding.title}
                </h3>

                {/* Description with animated reveal */}
                <motion.p
                  className="text-amber-100/90 text-base sm:text-lg leading-relaxed"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: prefersReducedMotion ? 0 : 0.5, duration: prefersReducedMotion ? 0.1 : 0.8 }}
                >
                  {finding.description}
                </motion.p>
              </div>
            </motion.div>

            {/* Remediation Steps - Always Expanded */}
            {finding.remediationSteps && finding.remediationSteps.length > 0 && (
              <motion.div
                variants={itemVariants}
                className="bg-black/30 backdrop-blur-sm rounded-xl p-5 sm:p-6 border border-amber-500/20"
              >
                <div className="flex items-center gap-3 mb-5">
                  <Terminal className="w-5 h-5 text-amber-300" />
                  <h4 className="text-lg font-semibold text-white">
                    Quick Setup Guide
                  </h4>
                </div>

                <ol className="space-y-4">
                  {finding.remediationSteps.map((step, index) => (
                    <motion.li
                      key={index}
                      className="flex items-start gap-4"
                      initial={{ opacity: 0, x: prefersReducedMotion ? 0 : -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: prefersReducedMotion ? 0 : (0.6 + index * 0.1), duration: prefersReducedMotion ? 0.1 : 0.4 }}
                    >
                      {/* Step number with glow */}
                      <motion.span
                        className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-amber-500 to-orange-600 rounded-full flex items-center justify-center text-white text-sm font-bold shadow-lg"
                        whileHover={prefersReducedMotion ? {} : { scale: 1.1 }}
                        animate={prefersReducedMotion ? {} : {
                          boxShadow: [
                            '0 0 10px rgba(245, 158, 11, 0.3)',
                            '0 0 20px rgba(245, 158, 11, 0.5)',
                            '0 0 10px rgba(245, 158, 11, 0.3)',
                          ],
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        {step.step}
                      </motion.span>

                      <div className="flex-1 pt-1">
                        <p className="text-white font-medium mb-2">{step.instruction}</p>
                        {step.code && (
                          <div className="flex items-center gap-2 flex-wrap">
                            <code className="flex-1 min-w-0 bg-black/50 text-amber-200 px-4 py-2.5 rounded-lg font-mono text-sm border border-amber-500/20 overflow-x-auto">
                              {step.code}
                            </code>
                            <motion.button
                              onClick={() => handleCopy(step.code!, index)}
                              className="flex-shrink-0 p-2.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/40 border border-amber-500/30 transition-all duration-200"
                              whileHover={prefersReducedMotion ? {} : { scale: 1.05 }}
                              whileTap={prefersReducedMotion ? {} : { scale: 0.95 }}
                              aria-label={`Copy command: ${step.code}`}
                            >
                              {copiedIndex === index ? (
                                <Check className="w-4 h-4 text-green-400" />
                              ) : (
                                <Copy className="w-4 h-4 text-amber-200" />
                              )}
                            </motion.button>
                          </div>
                        )}
                      </div>
                    </motion.li>
                  ))}
                </ol>
              </motion.div>
            )}

            {/* Reference Links */}
            {finding.references && finding.references.length > 0 && (
              <motion.div variants={itemVariants} className="mt-5 flex flex-wrap gap-3">
                {finding.references.map((link, index) => (
                  <motion.a
                    key={index}
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-sm text-amber-200 hover:text-white bg-amber-500/15 hover:bg-amber-500/30 px-4 py-2 rounded-lg border border-amber-500/30 hover:border-amber-400/50 transition-all duration-200"
                    whileHover={prefersReducedMotion ? {} : { scale: 1.02, y: -2 }}
                    whileTap={prefersReducedMotion ? {} : { scale: 0.98 }}
                  >
                    <ExternalLink className="w-4 h-4" />
                    <span>Documentation</span>
                  </motion.a>
                ))}
              </motion.div>
            )}

            {/* Scroll indicator - only show if there are more findings below */}
            {hasMoreFindings && (
              <motion.div
                className="flex justify-center mt-6"
                animate={prefersReducedMotion ? {} : { y: [0, 8, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              >
                <div className="flex flex-col items-center gap-1 text-amber-300/60">
                  <span className="text-xs uppercase tracking-wider">More findings below</span>
                  <ChevronDown className="w-5 h-5" />
                </div>
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
});
