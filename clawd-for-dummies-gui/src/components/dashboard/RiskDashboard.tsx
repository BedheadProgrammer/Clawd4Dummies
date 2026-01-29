import { memo } from 'react';
import { motion } from 'framer-motion';
import { RiskGauge } from './RiskGauge';
import { SeverityCounts } from './SeverityCounts';
import { useScanStore } from '../../stores/scanStore';
import { RISK_LEVEL_CONFIG, normalizeRiskLevel } from '../../types/scan';
import { Card } from '../common/Card';

export const RiskDashboard = memo(function RiskDashboard() {
  const { scanResult, status } = useScanStore();

  // Show placeholder when no results
  if (status !== 'complete' || !scanResult) {
    return (
      <Card className="text-center py-12">
        <div className="text-text-secondary">
          <p className="text-lg mb-2">No scan results yet</p>
          <p className="text-sm">Run a security scan to see your risk assessment</p>
        </div>
      </Card>
    );
  }

  const { overallRiskScore, riskLevel, criticalCount, highCount, mediumCount, lowCount, infoCount } = scanResult;
  // Normalize riskLevel to uppercase to match RISK_LEVEL_CONFIG keys
  const normalizedRiskLevel = normalizeRiskLevel(riskLevel);
  const config = RISK_LEVEL_CONFIG[normalizedRiskLevel];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="py-8">
        <div className="flex flex-col items-center">
          {/* Risk Gauge */}
          <RiskGauge score={overallRiskScore} riskLevel={normalizedRiskLevel} />

          {/* Risk Level Message */}
          <div className="text-center mt-6">
            <h2 className={`text-2xl font-display font-bold ${config.color}`}>
              {config.label}
            </h2>
            <p className={`text-lg ${config.color} mt-1`}>
              {config.message}
            </p>
          </div>

          {/* Severity Counts */}
          <SeverityCounts
            critical={criticalCount}
            high={highCount}
            medium={mediumCount}
            low={lowCount}
            info={infoCount}
          />
        </div>
      </Card>
    </motion.div>
  );
});
