"""
Finding model for security vulnerabilities and their attributes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class Severity(Enum):
    """Severity levels for security findings."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    def __str__(self) -> str:
        return self.value.upper()

    @property
    def color(self) -> str:
        colors = {
            Severity.CRITICAL: "red",
            Severity.HIGH: "orange",
            Severity.MEDIUM: "yellow",
            Severity.LOW: "green",
            Severity.INFO: "blue",
        }
        return colors.get(self, "white")

    @property
    def indicator(self) -> str:
        indicators = {
            Severity.CRITICAL: "[!]",
            Severity.HIGH: "[H]",
            Severity.MEDIUM: "[M]",
            Severity.LOW: "[L]",
            Severity.INFO: "[I]",
        }
        return indicators.get(self, "[?]")

    @property
    def description(self) -> str:
        descriptions = {
            Severity.CRITICAL: "Fix IMMEDIATELY - System is compromised",
            Severity.HIGH: "Fix within 24 hours - Serious risk",
            Severity.MEDIUM: "Fix within 1 week - Moderate risk",
            Severity.LOW: "Fix when convenient - Minor issue",
            Severity.INFO: "Informational - No action needed",
        }
        return descriptions.get(self, "Unknown severity")


class Category(Enum):
    """Categories of security findings."""

    PORT = "port"
    CREDENTIAL = "credential"
    CONFIG = "config"
    PROCESS = "process"
    PERMISSION = "permission"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    ENCRYPTION = "encryption"
    LOGGING = "logging"
    SANDBOX = "sandbox"
    COMMAND_INJECTION = "command_injection"
    ACCESS_CONTROL = "access_control"
    PROMPT_INJECTION = "prompt_injection"
    OTHER = "other"

    def __str__(self) -> str:
        return self.value

    @property
    def display_name(self) -> str:
        names = {
            Category.PORT: "Port Exposure",
            Category.CREDENTIAL: "Credential Exposure",
            Category.CONFIG: "Configuration Issue",
            Category.PROCESS: "Process Security",
            Category.PERMISSION: "File Permission",
            Category.NETWORK: "Network Exposure",
            Category.AUTHENTICATION: "Authentication",
            Category.ENCRYPTION: "Encryption",
            Category.LOGGING: "Logging",
            Category.SANDBOX: "Sandbox Security",
            Category.COMMAND_INJECTION: "Command Injection",
            Category.ACCESS_CONTROL: "Access Control",
            Category.PROMPT_INJECTION: "Prompt Injection",
            Category.OTHER: "Other",
        }
        return names.get(self, "Unknown")


@dataclass
class Finding:
    """Represents a security finding or vulnerability."""

    id: str
    title: str
    description: str
    severity: Severity
    category: Category
    cvss_score: float = 0.0
    evidence: Dict[str, Any] = field(default_factory=dict)
    location: str = ""
    remediation: str = ""
    remediation_steps: List[str] = field(default_factory=list)
    reference_links: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    scanner_version: str = "1.0.0"
    fix_prompt: str = ""

    def __post_init__(self):
        if not self.id:
            raise ValueError("Finding ID cannot be empty")
        if not self.title:
            raise ValueError("Finding title cannot be empty")
        if not 0.0 <= self.cvss_score <= 10.0:
            raise ValueError("CVSS score must be between 0.0 and 10.0")

    @property
    def is_critical(self) -> bool:
        return self.severity == Severity.CRITICAL

    @property
    def is_high(self) -> bool:
        return self.severity == Severity.HIGH

    @property
    def requires_immediate_action(self) -> bool:
        return self.severity in (Severity.CRITICAL, Severity.HIGH)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "category": self.category.value,
            "cvss_score": self.cvss_score,
            "evidence": self.evidence,
            "location": self.location,
            "remediation": self.remediation,
            "remediation_steps": self.remediation_steps,
            "reference_links": self.reference_links,
            "timestamp": self.timestamp.isoformat(),
            "scanner_version": self.scanner_version,
            "fix_prompt": self.fix_prompt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Finding":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            severity=Severity(data["severity"]),
            category=Category(data["category"]),
            cvss_score=data.get("cvss_score", 0.0),
            evidence=data.get("evidence", {}),
            location=data.get("location", ""),
            remediation=data.get("remediation", ""),
            remediation_steps=data.get("remediation_steps", []),
            reference_links=data.get("reference_links", []),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            scanner_version=data.get("scanner_version", "1.0.0"),
            fix_prompt=data.get("fix_prompt", ""),
        )

    def format_for_console(self) -> str:
        lines = [
            f"{self.severity.indicator} {self.severity.value.upper()}: {self.title}",
            f"   Category: {self.category.display_name}",
            f"   Risk Score: {self.cvss_score}/10",
            "",
            f"   {self.description}",
            "",
        ]

        if self.location:
            lines.append(f"   Location: {self.location}")
            lines.append("")

        if self.remediation:
            lines.append(f"   Remediation: {self.remediation}")
            lines.append("")

        if self.remediation_steps:
            lines.append("   Steps to fix:")
            for i, step in enumerate(self.remediation_steps, 1):
                lines.append(f"      {i}. {step}")
            lines.append("")

        if self.fix_prompt:
            lines.append("   AI Fix Prompt:")
            lines.append(f"      {self.fix_prompt}")
            lines.append("")

        if self.reference_links:
            lines.append("   Learn more:")
            for link in self.reference_links:
                lines.append(f"      - {link}")
            lines.append("")

        return "\n".join(lines)
