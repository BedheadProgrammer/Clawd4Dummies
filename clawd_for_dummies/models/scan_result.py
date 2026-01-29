"""
Scan result model for aggregating security scan findings.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any

from clawd_for_dummies.models.finding import Finding, Severity
from clawd_for_dummies.models.system_info import SystemInfo


class RiskLevel(Enum):
    """Overall risk levels for a complete scan."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SAFE = "safe"

    def __str__(self) -> str:
        return self.value.upper()

    @property
    def color(self) -> str:
        colors = {
            RiskLevel.CRITICAL: "red",
            RiskLevel.HIGH: "orange",
            RiskLevel.MEDIUM: "yellow",
            RiskLevel.LOW: "green",
            RiskLevel.SAFE: "blue",
        }
        return colors.get(self, "white")

    @property
    def indicator(self) -> str:
        indicators = {
            RiskLevel.CRITICAL: "[!]",
            RiskLevel.HIGH: "[H]",
            RiskLevel.MEDIUM: "[M]",
            RiskLevel.LOW: "[L]",
            RiskLevel.SAFE: "[OK]",
        }
        return indicators.get(self, "[?]")

    @property
    def message(self) -> str:
        messages = {
            RiskLevel.CRITICAL: "CRITICAL RISK - Immediate action required!",
            RiskLevel.HIGH: "HIGH RISK - Fix within 24 hours",
            RiskLevel.MEDIUM: "MEDIUM RISK - Fix within 1 week",
            RiskLevel.LOW: "LOW RISK - Minor issues found",
            RiskLevel.SAFE: "SAFE - No significant issues found",
        }
        return messages.get(self, "Unknown risk level")


@dataclass
class ScanResult:
    """Represents the complete result of a security scan."""

    scan_id: str
    timestamp: datetime
    duration_seconds: float
    system_info: SystemInfo
    findings: List[Finding] = field(default_factory=list)
    overall_risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.SAFE
    scanner_version: str = "1.0.0"

    def __post_init__(self):
        self._calculate_summary()

    def _calculate_summary(self) -> None:
        if not self.findings:
            self.overall_risk_score = 0.0
            self.risk_level = RiskLevel.SAFE
            return

        max_score = max(f.cvss_score for f in self.findings)
        avg_score = sum(f.cvss_score for f in self.findings) / len(self.findings)

        critical_count = self.critical_count
        high_count = self.high_count

        self.overall_risk_score = min(
            max_score * 0.6 + avg_score * 0.2 + (critical_count * 2 + high_count) * 0.2,
            10.0,
        )

        if self.overall_risk_score >= 9.0 or critical_count > 0:
            self.risk_level = RiskLevel.CRITICAL
        elif self.overall_risk_score >= 7.0 or high_count > 0:
            self.risk_level = RiskLevel.HIGH
        elif self.overall_risk_score >= 4.0:
            self.risk_level = RiskLevel.MEDIUM
        elif self.overall_risk_score >= 1.0:
            self.risk_level = RiskLevel.LOW
        else:
            self.risk_level = RiskLevel.SAFE

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.LOW)

    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.INFO)

    @property
    def total_count(self) -> int:
        return len(self.findings)

    @property
    def immediate_actions(self) -> List[str]:
        actions = []
        for finding in self.findings:
            if finding.requires_immediate_action:
                actions.append(finding.title)
        return actions

    def get_findings_by_severity(self, severity: Severity) -> List[Finding]:
        return [f for f in self.findings if f.severity == severity]

    def get_critical_findings(self) -> List[Finding]:
        return self.get_findings_by_severity(Severity.CRITICAL)

    def get_high_findings(self) -> List[Finding]:
        return self.get_findings_by_severity(Severity.HIGH)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scan_id": self.scan_id,
            "timestamp": self.timestamp.isoformat(),
            "duration_seconds": self.duration_seconds,
            "system_info": (
                self.system_info.to_dict()
                if hasattr(self.system_info, "to_dict")
                else {}
            ),
            "findings": [f.to_dict() for f in self.findings],
            "overall_risk_score": self.overall_risk_score,
            "risk_level": self.risk_level.value,
            "scanner_version": self.scanner_version,
            "summary": {
                "critical_count": self.critical_count,
                "high_count": self.high_count,
                "medium_count": self.medium_count,
                "low_count": self.low_count,
                "info_count": self.info_count,
                "total_count": self.total_count,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScanResult":
        from clawd_for_dummies.models.system_info import SystemInfo

        findings = [Finding.from_dict(f) for f in data.get("findings", [])]
        system_info = SystemInfo.from_dict(data.get("system_info", {}))

        return cls(
            scan_id=data["scan_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            duration_seconds=data["duration_seconds"],
            system_info=system_info,
            findings=findings,
            overall_risk_score=data.get("overall_risk_score", 0.0),
            risk_level=RiskLevel(data.get("risk_level", "safe")),
            scanner_version=data.get("scanner_version", "1.0.0"),
        )

    def format_summary(self) -> str:
        lines = [
            "=" * 60,
            f"{self.risk_level.indicator} OVERALL RISK: {self.risk_level.value.upper()}",
            f"   Risk Score: {self.overall_risk_score:.1f}/10",
            f"   {self.risk_level.message}",
            "",
            "FINDINGS SUMMARY:",
            f"   Critical: {self.critical_count}",
            f"   High:     {self.high_count}",
            f"   Medium:   {self.medium_count}",
            f"   Low:      {self.low_count}",
            f"   Info:     {self.info_count}",
            "",
        ]

        if self.immediate_actions:
            lines.append("IMMEDIATE ACTIONS REQUIRED:")
            for action in self.immediate_actions:
                lines.append(f"   - {action}")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)
