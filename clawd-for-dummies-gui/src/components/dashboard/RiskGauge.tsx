import { memo, useMemo } from 'react';
import { motion } from 'framer-motion';
import { RiskLevel, RISK_LEVEL_CONFIG, normalizeRiskLevel } from '../../types/scan';
import { colors } from '../../utils/theme';

interface RiskGaugeProps {
  score: number;
  riskLevel: RiskLevel;
}

export const RiskGauge = memo(function RiskGauge({ score, riskLevel }: RiskGaugeProps) {
  // Ensure score is a valid number, default to 0 if undefined/null
  const safeScore = typeof score === 'number' && !isNaN(score) ? score : 0;
  const percentage = (safeScore / 10) * 100;
  // Normalize riskLevel to uppercase to match RISK_LEVEL_CONFIG keys
  const normalizedRiskLevel = normalizeRiskLevel(riskLevel);
  const config = RISK_LEVEL_CONFIG[normalizedRiskLevel];

  // Calculate stroke color based on risk level
  const strokeColor = useMemo(() => {
    switch (normalizedRiskLevel) {
      case 'CRITICAL':
        return colors.critical;
      case 'HIGH':
        return colors.high;
      case 'MEDIUM':
        return colors.medium;
      case 'LOW':
        return colors.low;
      case 'SAFE':
        return colors.low;
      default:
        return colors.info;
    }
  }, [normalizedRiskLevel]);

  // SVG arc calculations
  const radius = 90;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative w-56 h-56">
      {/* Background circle */}
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="112"
          cy="112"
          r={radius}
          fill="none"
          stroke="rgba(125, 133, 144, 0.2)"
          strokeWidth="12"
        />
        {/* Animated progress arc */}
        <motion.circle
          cx="112"
          cy="112"
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />
      </svg>

      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className={`text-5xl font-display font-bold ${config.color}`}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.3 }}
        >
          {safeScore.toFixed(1)}
        </motion.span>
        <span className="text-text-secondary text-lg">/10</span>
        
        {/* Pulse animation for critical */}
        {normalizedRiskLevel === 'CRITICAL' && (
          <motion.div
            className="absolute inset-0 rounded-full border-4 border-critical"
            animate={{
              scale: [1, 1.1, 1],
              opacity: [0.5, 0, 0.5],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        )}
      </div>
    </div>
  );
});
