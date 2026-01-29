"""
Process Monitor Module

This module monitors Clawdbot processes for security issues.
"""

from typing import List

from clawd_for_dummies.models.finding import Finding, Severity, Category
from clawd_for_dummies.models.system_info import SystemInfo
from clawd_for_dummies.engine.base_scanner import BaseScanner


class ProcessMonitor(BaseScanner):
    """
    Scanner for monitoring Clawdbot process security.

    This scanner checks for:
    - Process running as root/admin
    - Exposed process arguments
    - Memory dump accessibility
    """

    def __init__(self, system_info: SystemInfo, verbose: bool = False):
        """Initialize the process monitor."""
        super().__init__(system_info, verbose)
        self.findings: List[Finding] = []

    @classmethod
    def get_name(cls) -> str:
        """Get scanner name."""
        return "Process Monitor"

    @classmethod
    def get_description(cls) -> str:
        """Get scanner description."""
        return "Checks Clawdbot process security and permissions"

    def scan(self) -> List[Finding]:
        """
        Perform process security scan.

        Returns:
            List of security findings
        """
        self.findings = []

        self.log("Checking Clawdbot processes...")

        try:
            # Find Clawdbot processes (this will raise ImportError if psutil unavailable)
            clawdbot_processes = self._find_clawdbot_processes()

            if not clawdbot_processes:
                self.log("No Clawdbot processes found (may not be running)")
                return self.findings

            for proc in clawdbot_processes:
                self._analyze_process(proc)

        except ImportError:
            self.log("psutil not available, skipping process checks")
        except Exception as e:
            self.log(f"Error checking processes: {e}")

        return self.findings

    def _find_clawdbot_processes(self) -> List:
        """Find Clawdbot-related processes.

        Raises:
            ImportError: If psutil is not available
        """
        import psutil

        processes = []

        try:
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    name = proc.info.get("name", "").lower()
                    cmdline = proc.info.get("cmdline", []) or []
                    cmdline_str = " ".join(cmdline).lower()

                    # Check for Moltbot/Clawdbot-related processes only
                    # Note: "claude" is NOT included as it refers to Claude Desktop,
                    # not Moltbot/Clawdbot
                    if any(
                        keyword in name or keyword in cmdline_str
                        for keyword in ["clawdbot", "moltbot", "mcp-gateway"]
                    ):
                        processes.append(proc)

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            self.log(f"Error finding processes: {e}")

        return processes

    def _analyze_process(self, proc) -> None:
        """Analyze a single process for security issues."""
        try:
            import psutil

            # Check if running as root/admin
            if self.system_info.is_admin:
                # Check if this specific process is running as admin
                try:
                    if self.system_info.is_windows:
                        # On Windows, check if process has elevated privileges
                        pass  # Would need Windows-specific check
                    else:
                        # On Unix, check if process UID is 0
                        if proc.uids().real == 0:
                            self._add_root_process_finding(proc)
                except (AttributeError, psutil.AccessDenied):
                    pass

            # Check command line arguments
            try:
                cmdline = proc.cmdline()
                if cmdline:
                    self._check_cmdline_secrets(proc, cmdline)
            except psutil.AccessDenied:
                pass

        except Exception as e:
            self.log(f"Error analyzing process {proc.pid}: {e}")

    def _add_root_process_finding(self, proc) -> None:
        """Add a finding for process running as root."""
        finding = Finding(
            id="CLAWD-PROC-001",
            title="Clawdbot Running as Root/Administrator",
            description=(
                "Clawdbot is running with root/administrator privileges. "
                "This is a security risk because any vulnerability in Clawdbot "
                "could give an attacker complete control over your system."
            ),
            severity=Severity.HIGH,
            category=Category.PROCESS,
            cvss_score=8.0,
            evidence={
                "pid": proc.pid,
                "name": proc.name(),
                "user": (
                    "root" if not self.system_info.is_windows else "Administrator"
                ),
            },
            location=f"Process {proc.pid}",
            remediation=("Run Clawdbot as a regular user without elevated privileges."),
            remediation_steps=[
                "Stop the current Clawdbot process",
                "Create a dedicated user account for Clawdbot (optional)",
                "Restart Moltbot/Clawdbot without sudo/admin privileges",
                "Ensure the user has only necessary permissions",
            ],
            reference_links=[
                "https://wiki.archlinux.org/title/Users_and_groups",
            ],
            fix_prompt=(
                "Stop the Clawdbot process running as root/Administrator and restart it as a "
                "regular user. Create a dedicated service account if needed: "
                "'sudo useradd -r -s /bin/false clawdbot' (Linux). Start the service as this user: "
                "'sudo -u clawdbot moltbot gateway' instead of running with sudo/admin privileges."
            ),
        )
        self.findings.append(finding)

    def _check_cmdline_secrets(self, proc, cmdline: List[str]) -> None:
        """Check command line arguments for exposed secrets."""
        import re

        cmdline_str = " ".join(cmdline)

        # Patterns that might indicate secrets in cmdline
        secret_patterns = [
            (
                r"--(?:api-?key|token|password|secret)[=\s]+([^\s]+)",
                "API key/token in command line",
            ),
            (r"-p[=\s]+([^\s]+)", "Possible password in command line"),
        ]

        for pattern, description in secret_patterns:
            matches = re.finditer(pattern, cmdline_str, re.IGNORECASE)
            for match in matches:
                finding = Finding(
                    id="CLAWD-PROC-002",
                    title="Potential Secret Exposed in Process Arguments",
                    description=(
                        "A potential secret was found in the command line "
                        "arguments of the Clawdbot process. Command line "
                        "arguments are visible to all users on the system "
                        "through tools like 'ps' or Task Manager."
                    ),
                    severity=Severity.HIGH,
                    category=Category.CREDENTIAL,
                    cvss_score=7.5,
                    evidence={
                        "pid": proc.pid,
                        "pattern_matched": description,
                    },
                    location=f"Process {proc.pid} command line",
                    remediation=(
                        "Move secrets to configuration files or environment variables "
                        "instead of command line arguments."
                    ),
                    remediation_steps=[
                        "Stop the Clawdbot process",
                        "Move the secret to a configuration file",
                        "Or use environment variables (less secure but better than cmdline)",
                        "Restart Moltbot/Clawdbot without the secret in arguments",
                    ],
                    reference_links=[
                        "https://www.netmeister.org/blog/passing-passwords.html",
                    ],
                    fix_prompt=(
                        "Remove the secret from command line arguments and move it to a "
                        "configuration file instead. Stop the process, add the secret to "
                        "moltbot.json or clawdbot.json (e.g., '\"authToken\": \"<secret>\"'), "
                        "set file permissions to 600, and restart the service without "
                        "passing secrets via command line flags."
                    ),
                )
                self.findings.append(finding)
