"""
Command-line interface for displaying scan results.
"""

from typing import List

from clawd_for_dummies.models.finding import Finding, Severity
from clawd_for_dummies.models.scan_result import ScanResult

# Priority finding ID - this finding should be displayed first prominently
PRIORITY_FINDING_ID = "CLAWD-INSTALL-001"


class CLI:
    """Console output formatter for scan results."""

    COLORS = {
        "red": "\033[91m",
        "orange": "\033[38;5;208m",
        "yellow": "\033[93m",
        "green": "\033[92m",
        "blue": "\033[94m",
        "white": "\033[97m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors

    def colorize(self, text: str, color: str) -> str:
        if not self.use_colors:
            return text

        color_code = self.COLORS.get(color, "")
        reset_code = self.COLORS["reset"]

        return f"{color_code}{text}{reset_code}"

    def _is_priority_finding(self, finding: Finding) -> bool:
        """Check if a finding is a priority finding that should be displayed first.

        Priority findings are specifically the 'Moltbot/Clawdbot Not Installed' message
        which should be prominently displayed to help users understand they need to
        install Moltbot/Clawdbot first.

        Detection logic:
        - Matches the specific finding ID "CLAWD-INSTALL-001"
        - OR matches titles that indicate installation/configuration is needed
          (must contain "moltbot" or "clawdbot" to avoid false positives)
        """
        # Check for the specific finding ID first
        if finding.id == PRIORITY_FINDING_ID:
            return True

        # Check for title patterns, but require "moltbot" or "clawdbot" context
        # to avoid false positives on unrelated findings
        title_lower = finding.title.lower()
        has_moltbot_context = "moltbot" in title_lower or "clawdbot" in title_lower
        is_installation_related = "not installed" in title_lower or "not configured" in title_lower

        return has_moltbot_context and is_installation_related

    def _get_priority_findings(self, findings: List[Finding]) -> List[Finding]:
        """Get all priority findings from the list."""
        return [f for f in findings if self._is_priority_finding(f)]

    def _get_regular_findings(self, findings: List[Finding]) -> List[Finding]:
        """Get all non-priority findings from the list."""
        return [f for f in findings if not self._is_priority_finding(f)]

    def _format_priority_finding(self, finding: Finding) -> str:
        """Format a priority finding with bold, prominent display."""
        lines = []

        # Banner width constants
        # The banner is 70 characters wide total (including | delimiters)
        # Inner width is 68 characters (70 - 2 for the | delimiters)
        banner_inner_width = 68
        # Title prefix "     ⚠️  " is 9 characters (5 spaces + emoji + 2 spaces)
        # Note: emoji may render as 1-2 chars in different terminals
        title_prefix = "     ⚠️  "
        title_prefix_len = 9
        # Available width for title text = inner width - prefix length - 1 (closing |)
        title_max_width = banner_inner_width - title_prefix_len - 1

        # Create a very visible, bold banner
        lines.append("")
        lines.append(self.colorize("+" + "=" * banner_inner_width + "+", "bold"))
        lines.append(self.colorize("|" + " " * banner_inner_width + "|", "bold"))
        lines.append(
            self.colorize(
                "|" + title_prefix + finding.title.upper().ljust(title_max_width) + "|",
                "bold",
            )
        )
        lines.append(self.colorize("|" + " " * banner_inner_width + "|", "bold"))
        lines.append(self.colorize("+" + "=" * banner_inner_width + "+", "bold"))
        lines.append("")

        # Description
        lines.append(self.colorize("   WHAT THIS MEANS:", "bold"))
        lines.append(f"   {finding.description}")
        lines.append("")

        # Remediation
        if finding.remediation:
            lines.append(self.colorize("   HOW TO FIX:", "bold"))
            lines.append(f"   {finding.remediation}")

        # Steps
        if finding.remediation_steps:
            lines.append("")
            for i, step in enumerate(finding.remediation_steps, 1):
                lines.append(f"      {i}. {step}")

        # Reference links
        if finding.reference_links:
            lines.append("")
            lines.append(self.colorize("   LEARN MORE:", "bold"))
            for link in finding.reference_links:
                lines.append(f"      - {link}")

        lines.append("")
        lines.append(self.colorize("+" + "=" * banner_inner_width + "+", "bold"))
        lines.append("")

        return "\n".join(lines)

    def format_scan_result(self, result: ScanResult) -> str:
        lines = []

        lines.append(self._format_header())
        lines.append("")

        lines.append(self._format_system_info(result.system_info))
        lines.append("")

        lines.append(self._format_overall_risk(result))
        lines.append("")

        if result.findings:
            lines.append(self._format_findings(result))
        else:
            lines.append(
                self.colorize(
                    "[OK] No security issues found! Your system looks safe.",
                    "green",
                )
            )
            lines.append("")

        lines.append(self._format_footer(result))

        return "\n".join(lines)

    def _format_header(self) -> str:
        header = """
+====================================================================+
|           CLAWD FOR DUMMIES - Security Scan Results                |
+====================================================================+
"""
        return header

    def _format_system_info(self, system_info) -> str:
        lines = [
            self.colorize("SYSTEM INFORMATION:", "bold"),
            f"  Platform: {system_info.platform_display}",
            f"  User: {system_info.username}",
            f"  Admin Privileges: {'Yes' if system_info.is_admin else 'No'}",
        ]

        if system_info.local_ips:
            lines.append(f"  Local IPs: {', '.join(system_info.local_ips[:3])}")

        return "\n".join(lines)

    def _format_overall_risk(self, result: ScanResult) -> str:
        color = result.risk_level.color
        indicator = result.risk_level.indicator

        lines = [
            "=" * 66,
            self.colorize(
                f"{indicator} OVERALL RISK: {result.risk_level.value.upper()}",
                color,
            ),
            self.colorize(f"   Risk Score: {result.overall_risk_score:.1f}/10", color),
            self.colorize(f"   {result.risk_level.message}", color),
            "=" * 66,
        ]

        return "\n".join(lines)

    def _format_findings(self, result: ScanResult) -> str:
        lines = []

        # First, check for priority findings (like "Moltbot/Clawdbot Not Installed")
        # These should be displayed FIRST, prominently
        priority_findings = self._get_priority_findings(result.findings)

        if priority_findings:
            for finding in priority_findings:
                lines.append(self._format_priority_finding(finding))

        lines.append(self.colorize("FINDINGS SUMMARY:", "bold"))
        lines.append(f"   Critical: {result.critical_count}")
        lines.append(f"   High:     {result.high_count}")
        lines.append(f"   Medium:   {result.medium_count}")
        lines.append(f"   Low:      {result.low_count}")
        lines.append(f"   Info:     {result.info_count}")
        lines.append("")

        # Get regular (non-priority) findings for each severity level
        regular_findings = self._get_regular_findings(result.findings)

        critical_findings = [f for f in regular_findings if f.severity == Severity.CRITICAL]
        high_findings = [f for f in regular_findings if f.severity == Severity.HIGH]
        medium_findings = [f for f in regular_findings if f.severity == Severity.MEDIUM]
        low_findings = [f for f in regular_findings if f.severity == Severity.LOW]
        info_findings = [f for f in regular_findings if f.severity == Severity.INFO]

        if critical_findings:
            lines.append(self.colorize("[!] CRITICAL ISSUES (Fix IMMEDIATELY):", "red"))
            lines.append("")
            for finding in critical_findings:
                lines.append(self._format_finding(finding))
            lines.append("")

        if high_findings:
            lines.append(
                self.colorize("[H] HIGH ISSUES (Fix within 24 hours):", "orange")
            )
            lines.append("")
            for finding in high_findings:
                lines.append(self._format_finding(finding))
            lines.append("")

        if medium_findings:
            lines.append(
                self.colorize("[M] MEDIUM ISSUES (Fix within 1 week):", "yellow")
            )
            lines.append("")
            for finding in medium_findings:
                lines.append(self._format_finding(finding))
            lines.append("")

        if low_findings:
            lines.append(self.colorize("[L] LOW ISSUES (Fix when convenient):", "green"))
            lines.append("")
            for finding in low_findings:
                lines.append(self._format_finding(finding))
            lines.append("")

        if info_findings:
            lines.append(self.colorize("[I] INFORMATIONAL:", "blue"))
            lines.append("")
            for finding in info_findings:
                lines.append(self._format_finding(finding))
            lines.append("")

        return "\n".join(lines)

    def _format_finding(self, finding: Finding) -> str:
        color = finding.severity.color
        indicator = finding.severity.indicator

        lines = [
            self.colorize(f"{indicator} {finding.title}", color),
            f"   {finding.description}",
        ]

        if finding.location:
            lines.append(f"   Location: {finding.location}")

        if finding.remediation:
            lines.append("")
            lines.append(self.colorize("   HOW TO FIX:", "bold"))
            lines.append(f"   {finding.remediation}")

        if finding.remediation_steps:
            for i, step in enumerate(finding.remediation_steps, 1):
                lines.append(f"      {i}. {step}")

        if finding.reference_links:
            lines.append("")
            lines.append("   Learn more:")
            for link in finding.reference_links:
                lines.append(f"      - {link}")

        lines.append("")

        return "\n".join(lines)

    def _format_footer(self, result: ScanResult) -> str:
        lines = [
            "=" * 66,
            f"Scan completed in {result.duration_seconds:.2f} seconds",
            f"Scanner version: {result.scanner_version}",
            "",
            "For more information, visit:",
            "  https://github.com/yourusername/clawd-for-dummies",
            "=" * 66,
        ]

        return "\n".join(lines)

    def format_moltbot_not_found_message(self) -> str:
        """Format a user-friendly message when Moltbot is not installed/running."""
        lines = []
        lines.append("")
        lines.append(self.colorize("╔═══════════════════════════════════════════════════════════════╗", "yellow"))
        lines.append(self.colorize("║           Moltbot/Clawdbot Not Detected                       ║", "yellow"))
        lines.append(self.colorize("╚═══════════════════════════════════════════════════════════════╝", "yellow"))
        lines.append("")
        lines.append("  We couldn't find a running Moltbot or Clawdbot instance.")
        lines.append("")
        lines.append(self.colorize("  📋 WHAT THIS MEANS:", "bold"))
        lines.append("     Moltbot (or Clawdbot) is not currently running on your")
        lines.append("     computer, or it may not be installed yet.")
        lines.append("")
        lines.append(self.colorize("  🔧 HOW TO INSTALL MOLTBOT:", "bold"))
        lines.append("")
        lines.append(self.colorize("     Step 1:", "blue") + " Install Node.js (version 22 or higher)")
        lines.append("             Download from: https://nodejs.org/")
        lines.append("")
        lines.append(self.colorize("     Step 2:", "blue") + " Install Moltbot globally")
        lines.append("             npm install -g moltbot@latest")
        lines.append("")
        lines.append(self.colorize("     Step 3:", "blue") + " Run the onboarding wizard")
        lines.append("             moltbot onboard --install-daemon")
        lines.append("")
        lines.append(self.colorize("     Step 4:", "blue") + " Start the gateway")
        lines.append("             moltbot gateway --port 18789")
        lines.append("")
        lines.append(self.colorize("  📚 DOCUMENTATION:", "bold"))
        lines.append("     • Getting Started: https://docs.molt.bot/start/getting-started")
        lines.append("     • Installation:    https://docs.molt.bot/install")
        lines.append("     • GitHub:          https://github.com/moltbot/moltbot")
        lines.append("")
        lines.append(self.colorize("  💡 TIP:", "green"))
        lines.append("     You can still run the local security scan without Moltbot")
        lines.append("     connected. The scanner will check for potential vulnerabilities")
        lines.append("     in configuration files on your system.")
        lines.append("")
        return "\n".join(lines)

    def format_connection_error(self, error: str, message: str = "") -> str:
        """Format a user-friendly connection error message."""
        lines = []
        lines.append("")
        lines.append(self.colorize("╔═══════════════════════════════════════════════════════════════╗", "red"))
        lines.append(self.colorize("║                    Connection Error                           ║", "red"))
        lines.append(self.colorize("╚═══════════════════════════════════════════════════════════════╝", "red"))
        lines.append("")
        lines.append(f"  {self.colorize('Error:', 'bold')} {error}")
        if message:
            lines.append(f"  {self.colorize('Details:', 'bold')} {message}")
        lines.append("")
        lines.append("  For help, visit: https://github.com/moltbot/moltbot")
        lines.append("")
        return "\n".join(lines)
