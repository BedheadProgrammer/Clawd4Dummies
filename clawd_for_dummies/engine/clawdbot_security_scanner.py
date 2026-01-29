"""
Clawdbot/Moltbot Security Scanner Module

This module performs security checks for Clawdbot and Moltbot
(https://github.com/moltbot/moltbot) configurations:
- DM policy configuration
- Sandbox settings
- Prompt injection risks
- Dangerous command blocking
- Docker network isolation
- MCP tools access restrictions
- Audit logging configuration
- Pairing code security

Note: Moltbot is the successor to Clawdbot. Both are supported.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from clawd_for_dummies.models.finding import Finding, Severity, Category
from clawd_for_dummies.models.system_info import SystemInfo
from clawd_for_dummies.engine.base_scanner import BaseScanner


class ClawdbotSecurityScanner(BaseScanner):
    """
    Scanner for Clawdbot/Moltbot security configurations.

    Supports both Clawdbot (legacy) and Moltbot (https://github.com/moltbot/moltbot).

    This scanner checks for:
    - DM policy allowing all users
    - Sandbox disabled by default
    - Prompt injection vulnerabilities
    - Dangerous commands unblocked
    - Missing Docker network isolation
    - Elevated MCP tools access
    - Missing audit/session logging
    - Weak/default pairing codes
    """

    # Known dangerous commands that should be blocked
    DANGEROUS_COMMANDS = [
        "rm -rf",
        "rm -r /",
        "rm -rf /",
        "rm -rf ~",
        ":(){ :|:& };:",  # Fork bomb
        "mkfs",
        "dd if=",
        "> /dev/sda",
        "chmod -R 777 /",
        "curl | bash",
        "curl | sh",
        "wget | bash",
        "wget | sh",
        "pip install --user",
        "sudo rm",
        "sudo chmod",
    ]

    def __init__(self, system_info: SystemInfo, verbose: bool = False):
        """Initialize the Clawdbot security scanner."""
        super().__init__(system_info, verbose)
        self.findings: List[Finding] = []

    @classmethod
    def get_name(cls) -> str:
        """Get scanner name."""
        return "Clawdbot/Moltbot Security Scanner"

    @classmethod
    def get_description(cls) -> str:
        """Get scanner description."""
        return "Checks Clawdbot/Moltbot security configurations and vulnerabilities"

    def scan(self) -> List[Finding]:
        """
        Perform Clawdbot security scan.

        Returns:
            List of security findings
        """
        self.findings = []

        self.log("Scanning for Clawdbot-specific security issues...")

        # Find and analyze config files
        config_files = self._find_config_files()

        for config_file in config_files:
            self.analyze_config_file(config_file)

        if not config_files:
            self.log("No Clawdbot configuration files found")
            # Add an info finding to let the user know Moltbot/Clawdbot is not installed
            finding = Finding(
                id="CLAWD-INSTALL-001",
                title="Moltbot/Clawdbot Not Installed or Not Configured",
                description=(
                    "No Moltbot or Clawdbot configuration files were found on your system. "
                    "This likely means Moltbot/Clawdbot is not installed or has not been configured yet. "
                    "If you intended to scan Moltbot/Clawdbot security, you will need to install it first."
                ),
                severity=Severity.INFO,
                category=Category.CONFIG,
                cvss_score=0.0,
                evidence={
                    "searched_locations": "Platform-specific config directories",
                    "config_files_found": 0,
                },
                location="System configuration",
                remediation=(
                    "Install Moltbot to use the full security scanning capabilities."
                ),
                remediation_steps=[
                    "Install Node.js (version 22 or higher) from https://nodejs.org/",
                    "Run: npm install -g moltbot@latest",
                    "Run: moltbot onboard --install-daemon",
                    "Start the gateway: moltbot gateway --port 18789",
                    "Run this scanner again to check your Moltbot security configuration",
                ],
                reference_links=[
                    "https://docs.molt.bot/start/getting-started",
                    "https://docs.molt.bot/install",
                    "https://github.com/moltbot/moltbot",
                ],
                fix_prompt=(
                    "Install Moltbot by running: 'npm install -g moltbot@latest' (requires Node.js 22+). "
                    "Then run 'moltbot onboard --install-daemon' to set up the configuration. "
                    "After installation, run this scanner again to check your security configuration."
                ),
            )
            self.findings.append(finding)

        return self.findings

    def _find_config_files(self) -> List[Path]:
        """Find Clawdbot/Moltbot configuration files.

        Searches for configuration files in the following order of precedence:
        1. Environment variable overrides (MOLTBOT_CONFIG_PATH, CLAWDBOT_CONFIG_PATH)
        2. State directory overrides (MOLTBOT_STATE_DIR, CLAWDBOT_STATE_DIR)
        3. New moltbot paths (~/.moltbot/)
        4. Legacy clawdbot paths (~/.clawdbot/)
        5. Platform-specific application paths
        6. Common configuration file names

        This matches the path resolution logic from the official moltbot repository:
        https://github.com/moltbot/moltbot
        """
        config_files: List[Path] = []
        seen_paths: set[Path] = set()  # Track already-seen paths to avoid duplicates
        home = Path(self.system_info.home_directory)
        paths: List[Path] = []

        # Check for explicit config path overrides via environment variables
        # (matches moltbot's resolveConfigPathCandidate behavior)
        explicit_config = (
            os.environ.get("MOLTBOT_CONFIG_PATH", "").strip()
            or os.environ.get("CLAWDBOT_CONFIG_PATH", "").strip()
        )
        if explicit_config:
            explicit_path = Path(os.path.expanduser(explicit_config))
            # Validate it's a file (not a directory) before returning
            if explicit_path.exists() and explicit_path.is_file():
                return [explicit_path]

        # Check for state directory overrides via environment variables
        moltbot_state_dir = os.environ.get("MOLTBOT_STATE_DIR", "").strip()
        clawdbot_state_dir = os.environ.get("CLAWDBOT_STATE_DIR", "").strip()

        if moltbot_state_dir:
            state_path = Path(os.path.expanduser(moltbot_state_dir))
            paths.extend([
                state_path / "moltbot.json",
                state_path / "clawdbot.json",
                state_path / "config.json",
                state_path / "settings.json",
            ])

        if clawdbot_state_dir:
            state_path = Path(os.path.expanduser(clawdbot_state_dir))
            paths.extend([
                state_path / "moltbot.json",
                state_path / "clawdbot.json",
                state_path / "config.json",
                state_path / "settings.json",
            ])

        # Default moltbot/clawdbot state directories (cross-platform)
        # These are the canonical paths used by moltbot:
        # - ~/.moltbot/ (new default)
        # - ~/.clawdbot/ (legacy default)
        moltbot_dir = home / ".moltbot"
        clawdbot_dir = home / ".clawdbot"

        # Add paths from both directories with both config filenames
        # Order: new dir first, then legacy dir; new filename first, then legacy
        paths.extend([
            # New moltbot directory with both config filenames
            moltbot_dir / "moltbot.json",
            moltbot_dir / "clawdbot.json",
            moltbot_dir / "config.json",
            moltbot_dir / "settings.json",
            # Legacy clawdbot directory with both config filenames
            clawdbot_dir / "moltbot.json",
            clawdbot_dir / "clawdbot.json",
            clawdbot_dir / "config.json",
            clawdbot_dir / "settings.json",
        ])

        # Platform-specific paths for Moltbot and Clawdbot
        if self.system_info.is_windows:
            appdata = os.environ.get("APPDATA", "").strip()
            localappdata = os.environ.get("LOCALAPPDATA", "").strip()
            # Only add paths if environment variables are set
            if appdata:
                paths.extend([
                    # Moltbot paths (primary)
                    Path(appdata) / "Moltbot" / "moltbot.json",
                    Path(appdata) / "Moltbot" / "clawdbot.json",
                    Path(appdata) / "Moltbot" / "settings.json",
                    Path(appdata) / "Moltbot" / "config.json",
                    # Clawdbot paths (Windows app data)
                    Path(appdata) / "Clawdbot" / "moltbot.json",
                    Path(appdata) / "Clawdbot" / "clawdbot.json",
                    Path(appdata) / "Clawdbot" / "settings.json",
                    Path(appdata) / "Clawdbot" / "config.json",
                    # Note: Claude Desktop paths (Claude/) are NOT scanned here
                    # as they are for the Claude Desktop App, not Moltbot/Clawdbot
                ])
            if localappdata:
                paths.extend([
                    Path(localappdata) / "Moltbot" / "moltbot.json",
                    Path(localappdata) / "Moltbot" / "settings.json",
                ])
        elif self.system_info.is_macos:
            app_support = home / "Library" / "Application Support"
            paths.extend([
                # Moltbot paths (primary)
                app_support / "Moltbot" / "moltbot.json",
                app_support / "Moltbot" / "clawdbot.json",
                app_support / "Moltbot" / "settings.json",
                app_support / "Moltbot" / "config.json",
                # Clawdbot paths (macOS Application Support)
                app_support / "Clawdbot" / "moltbot.json",
                app_support / "Clawdbot" / "clawdbot.json",
                app_support / "Clawdbot" / "settings.json",
                app_support / "Clawdbot" / "config.json",
                # Note: Claude Desktop paths (Claude/) are NOT scanned here
                # as they are for the Claude Desktop App, not Moltbot/Clawdbot
            ])
        else:  # Linux
            config_dir = home / ".config"
            paths.extend([
                # Moltbot XDG config paths
                config_dir / "moltbot" / "moltbot.json",
                config_dir / "moltbot" / "clawdbot.json",
                config_dir / "moltbot" / "settings.json",
                config_dir / "moltbot" / "config.json",
                # Clawdbot XDG config paths
                config_dir / "clawdbot" / "moltbot.json",
                config_dir / "clawdbot" / "clawdbot.json",
                config_dir / "clawdbot" / "settings.json",
                config_dir / "clawdbot" / "config.json",
                # Note: Claude Desktop paths (.claude/, .config/claude/) are NOT
                # scanned here as they are for the Claude Desktop App, not Moltbot
            ])

        # Common files (both Moltbot and Clawdbot)
        paths.extend([
            # Moltbot common files
            home / "moltbot.json",
            home / "moltbot_config.json",
            Path("moltbot.json"),
            Path("moltbot_config.json"),
            # Clawdbot common files
            home / "clawdbot.json",
            home / "clawdbot_config.json",
            Path("clawdbot.json"),
            Path("clawdbot_config.json"),
            # MCP config files
            Path("mcp_config.json"),
            Path(".mcp") / "config.json",
            home / ".mcp" / "config.json",
            # Note: claude_desktop_config.json is NOT scanned here as it is
            # for the Claude Desktop App, not Moltbot/Clawdbot
        ])

        for path in paths:
            # Check existence once and ensure it's a file (not a directory)
            if path.exists() and path.is_file():
                resolved = path.resolve()
                if resolved not in seen_paths:
                    seen_paths.add(resolved)
                    config_files.append(path)

        return config_files

    def analyze_config_file(self, config_file: Path) -> None:
        """Analyze a single configuration file for security issues."""
        self.log(f"Analyzing {config_file}...")

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Check for various security settings
            self._check_dm_policy(config, config_file)
            self._check_sandbox_settings(config, config_file)
            self._check_dangerous_commands(config, config_file)
            self._check_docker_network_isolation(config, config_file)
            self._check_mcp_tools_access(config, config_file)
            self._check_audit_logging(config, config_file)
            self._check_pairing_codes(config, config_file)
            self._check_prompt_injection_protection(config, config_file)

        except json.JSONDecodeError:
            self.log(f"Invalid JSON in {config_file}")
        except Exception as e:
            self.log(f"Error analyzing {config_file}: {e}")

    def _check_dm_policy(self, config: Dict[str, Any], config_file: Path) -> None:
        """Check DM policy configuration."""
        dm_policy = None

        # Check various possible locations for DM policy
        if "dm" in config and isinstance(config["dm"], dict):
            dm_policy = config["dm"].get("policy")

        if dm_policy is None and "security" in config:
            if isinstance(config["security"], dict):
                dm_policy = config["security"].get("dmPolicy")

        if dm_policy is None:
            dm_policy = config.get("dmPolicy")

        # Check for overly permissive DM policy
        if dm_policy in ["all", "*", "allow_all", "any"]:
            finding = Finding(
                id="CLAWD-DM-001",
                title="DM Policy Allows All Users",
                description=(
                    "Your Clawdbot DM (direct message) policy is set to allow all users. "
                    "This means anyone can send commands to your Clawdbot instance via "
                    "direct messages, which could lead to unauthorized access or abuse."
                ),
                severity=Severity.HIGH,
                category=Category.ACCESS_CONTROL,
                cvss_score=7.5,
                evidence={
                    "config_file": str(config_file),
                    "dm_policy": dm_policy,
                },
                location=str(config_file),
                remediation=(
                    "Set a DM policy allow list to restrict who can interact with your "
                    "Clawdbot instance via direct messages."
                ),
                remediation_steps=[
                    f"Open {config_file}",
                    "Find the 'dm' or 'security' section",
                    "Change 'dmPolicy' from 'all' to a specific allow list",
                    'Example: "dmPolicy": ["user1@example.com", "user2@example.com"]',
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://github.com/jasondsmith72/Clawdbot",
                ],
                fix_prompt=(
                    f"Restrict DM policy in '{config_file.name}' by replacing 'all' with a "
                    f"specific allow list. Set '\"dmPolicy\": [\"your-email@example.com\"]' "
                    f"to only allow your own email. Add other trusted users as needed. "
                    f"Restart the service after changes."
                ),
            )
            self.findings.append(finding)

    def _check_sandbox_settings(
        self, config: Dict[str, Any], config_file: Path
    ) -> None:
        """Check sandbox configuration."""
        sandbox_enabled = None
        docker_network = None

        # Check for sandbox settings
        if "sandbox" in config:
            if isinstance(config["sandbox"], dict):
                sandbox_enabled = config["sandbox"].get("enabled")
                docker_network = config["sandbox"].get("network")
            else:
                sandbox_enabled = config["sandbox"]

        if sandbox_enabled is None and "security" in config:
            if isinstance(config["security"], dict):
                sandbox_enabled = config["security"].get("sandbox")

        # Check if sandbox is disabled
        if sandbox_enabled is False or sandbox_enabled == "none":
            finding = Finding(
                id="CLAWD-SANDBOX-001",
                title="Sandbox Disabled",
                description=(
                    "Your Clawdbot sandbox is disabled. The sandbox provides isolation "
                    "between code execution and your host system, preventing malicious "
                    "code from accessing your files or system resources. Without it, "
                    "any code executed by Clawdbot has full access to your system."
                ),
                severity=Severity.CRITICAL,
                category=Category.SANDBOX,
                cvss_score=9.0,
                evidence={
                    "config_file": str(config_file),
                    "sandbox_enabled": sandbox_enabled,
                },
                location=str(config_file),
                remediation=(
                    "Enable the sandbox with full isolation and Docker network disabled."
                ),
                remediation_steps=[
                    f"Open {config_file}",
                    "Set 'sandbox' configuration to:",
                    '  "sandbox": {',
                    '    "enabled": true,',
                    '    "mode": "all",',
                    '    "network": "none"',
                    "  }",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://github.com/jasondsmith72/Clawdbot",
                ],
                fix_prompt=(
                    f"Enable the sandbox in '{config_file.name}' by adding: "
                    f"'\"sandbox\": {{\"enabled\": true, \"mode\": \"all\", \"network\": \"none\"}}'. "
                    f"This isolates code execution from your host system and prevents network "
                    f"access from sandboxed code. Restart the service after changes."
                ),
            )
            self.findings.append(finding)

        # Check Docker network isolation
        if docker_network and docker_network != "none":
            finding = Finding(
                id="CLAWD-SANDBOX-002",
                title="Docker Network Not Isolated",
                description=(
                    f"Your sandbox Docker network is set to '{docker_network}' instead of "
                    "'none'. This allows code running in the sandbox to make network "
                    "connections, which could be used to exfiltrate data or connect to "
                    "malicious servers."
                ),
                severity=Severity.HIGH,
                category=Category.SANDBOX,
                cvss_score=7.0,
                evidence={
                    "config_file": str(config_file),
                    "docker_network": docker_network,
                },
                location=str(config_file),
                remediation=(
                    "Set the sandbox Docker network to 'none' for full isolation."
                ),
                remediation_steps=[
                    f"Open {config_file}",
                    "In the sandbox configuration, set:",
                    '  "network": "none"',
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://docs.docker.com/network/",
                ],
                fix_prompt=(
                    f"Set the sandbox network to 'none' in '{config_file.name}' by updating "
                    f"the sandbox configuration: '\"sandbox\": {{\"network\": \"none\"}}'. "
                    f"This prevents sandboxed code from making any network connections. "
                    f"Restart the service after changes."
                ),
            )
            self.findings.append(finding)

    def _check_dangerous_commands(
        self, config: Dict[str, Any], config_file: Path
    ) -> None:
        """Check for dangerous command blocking."""
        blocked_commands = None

        # Check for command blocking settings
        if "commands" in config and isinstance(config["commands"], dict):
            blocked_commands = config["commands"].get("blocked", [])

        if blocked_commands is None and "security" in config:
            if isinstance(config["security"], dict):
                blocked_commands = config["security"].get("blockedCommands", [])

        # Check if dangerous commands are not blocked
        dangerous_not_blocked = []
        if blocked_commands is not None:
            for dangerous_cmd in self.DANGEROUS_COMMANDS:
                if dangerous_cmd not in blocked_commands:
                    dangerous_not_blocked.append(dangerous_cmd)
        else:
            dangerous_not_blocked = self.DANGEROUS_COMMANDS.copy()

        if dangerous_not_blocked:
            finding = Finding(
                id="CLAWD-CMD-001",
                title="Dangerous Commands Not Blocked",
                description=(
                    "Your Clawdbot configuration does not block dangerous shell commands. "
                    "Commands like 'rm -rf' or piped curl/wget can cause severe damage to "
                    "your system or be used to download and execute malicious scripts. "
                    f"Found {len(dangerous_not_blocked)} unblocked dangerous patterns."
                ),
                severity=Severity.CRITICAL,
                category=Category.COMMAND_INJECTION,
                cvss_score=9.5,
                evidence={
                    "config_file": str(config_file),
                    "unblocked_commands": dangerous_not_blocked[:5],  # Show first 5
                    "total_unblocked": len(dangerous_not_blocked),
                },
                location=str(config_file),
                remediation=("Add dangerous commands to the blocked commands list."),
                remediation_steps=[
                    f"Open {config_file}",
                    "Add a 'commands' section with blocked patterns:",
                    '  "commands": {',
                    '    "blocked": [',
                    '      "rm -rf",',
                    '      "curl | bash",',
                    '      "curl | sh",',
                    '      "wget | bash",',
                    '      "mkfs"',
                    "    ]",
                    "  }",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://owasp.org/www-community/attacks/Command_Injection",
                ],
                fix_prompt=(
                    f"Block dangerous commands in '{config_file.name}' by adding: "
                    f"'\"commands\": {{\"blocked\": [\"rm -rf\", \"curl | bash\", \"curl | sh\", "
                    f"\"wget | bash\", \"wget | sh\", \"mkfs\", \"dd if=\", \"chmod -R 777 /\"]}}'. "
                    f"This prevents execution of destructive commands. Restart the service after changes."
                ),
            )
            self.findings.append(finding)

    def _check_docker_network_isolation(
        self, config: Dict[str, Any], config_file: Path
    ) -> None:
        """Check for Docker network isolation."""
        network_mode = None

        if "docker" in config and isinstance(config["docker"], dict):
            network_mode = config["docker"].get("network")

        if network_mode is None and "container" in config:
            if isinstance(config["container"], dict):
                network_mode = config["container"].get("network")

        if network_mode and network_mode not in ["none", "isolated"]:
            finding = Finding(
                id="CLAWD-DOCKER-001",
                title="No Docker Network Isolation",
                description=(
                    f"Your Docker network mode is set to '{network_mode}'. Without proper "
                    "network isolation, containers can communicate with external services "
                    "and potentially exfiltrate data or download malicious content."
                ),
                severity=Severity.HIGH,
                category=Category.NETWORK,
                cvss_score=7.5,
                evidence={
                    "config_file": str(config_file),
                    "network_mode": network_mode,
                },
                location=str(config_file),
                remediation=(
                    "Use Docker network isolation by setting network mode to 'none'."
                ),
                remediation_steps=[
                    f"Open {config_file}",
                    "Set Docker network to isolated mode:",
                    '  "docker": {',
                    '    "network": "none"',
                    "  }",
                    "Or use a custom isolated network",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://docs.docker.com/network/",
                ],
                fix_prompt=(
                    f"Set Docker network isolation in '{config_file.name}' by updating: "
                    f"'\"docker\": {{\"network\": \"none\"}}'. This prevents containers from "
                    f"making any network connections. Alternatively, create a custom isolated "
                    f"Docker network. Restart the service after changes."
                ),
            )
            self.findings.append(finding)

    def _check_mcp_tools_access(
        self, config: Dict[str, Any], config_file: Path
    ) -> None:
        """Check for elevated MCP tools access."""
        tool_permissions = None

        if "mcp" in config and isinstance(config["mcp"], dict):
            tool_permissions = config["mcp"].get("permissions")

        if tool_permissions is None and "tools" in config:
            if isinstance(config["tools"], dict):
                tool_permissions = config["tools"].get("permissions")

        # Check for elevated permissions
        if tool_permissions in ["all", "*", "elevated", "admin"]:
            finding = Finding(
                id="CLAWD-MCP-001",
                title="Elevated MCP Tools Access Granted",
                description=(
                    "Your MCP (Model Control Protocol) tools configuration grants elevated "
                    "or unrestricted access. This allows Moltbot/Clawdbot to use all available "
                    "tools without restrictions, which could lead to unintended system "
                    "modifications or data access."
                ),
                severity=Severity.HIGH,
                category=Category.ACCESS_CONTROL,
                cvss_score=8.0,
                evidence={
                    "config_file": str(config_file),
                    "tool_permissions": tool_permissions,
                },
                location=str(config_file),
                remediation=(
                    "Restrict MCP tools to the minimum needed for your use case."
                ),
                remediation_steps=[
                    f"Open {config_file}",
                    "Review which MCP tools are actually needed",
                    "Set 'permissions' to a restricted list:",
                    '  "tools": {',
                    '    "permissions": "restricted",',
                    '    "allowed": ["read_file", "list_directory"]',
                    "  }",
                    "Remove tools that are not necessary",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://modelcontextprotocol.io/",
                ],
                fix_prompt=(
                    f"Restrict MCP tools access in '{config_file.name}' by changing permissions "
                    f"from '{tool_permissions}' to a restricted allow list: "
                    f"'\"tools\": {{\"permissions\": \"restricted\", \"allowed\": [\"read_file\", "
                    f"\"list_directory\"]}}'. Only include tools you actually need. "
                    f"Restart the service after changes."
                ),
            )
            self.findings.append(finding)

    def _check_audit_logging(self, config: Dict[str, Any], config_file: Path) -> None:
        """Check for audit/session logging configuration."""
        audit_enabled = None
        session_logging = None

        if "logging" in config and isinstance(config["logging"], dict):
            audit_enabled = config["logging"].get("audit")
            session_logging = config["logging"].get("session")

        if audit_enabled is None and "security" in config:
            if isinstance(config["security"], dict):
                audit_enabled = config["security"].get("auditLog")

        if session_logging is None and "security" in config:
            if isinstance(config["security"], dict):
                session_logging = config["security"].get("sessionLogging")

        if audit_enabled is False or (
            audit_enabled is None and session_logging is None
        ):
            finding = Finding(
                id="CLAWD-AUDIT-001",
                title="No Audit Logs Enabled",
                description=(
                    "Audit logging is not enabled in your Clawdbot configuration. "
                    "Without audit logs, you cannot track what commands were executed, "
                    "when they were run, or detect unauthorized access or suspicious "
                    "activity on your system."
                ),
                severity=Severity.MEDIUM,
                category=Category.LOGGING,
                cvss_score=5.0,
                evidence={
                    "config_file": str(config_file),
                    "audit_enabled": audit_enabled,
                    "session_logging": session_logging,
                },
                location=str(config_file),
                remediation=("Enable audit and session logging to track all activity."),
                remediation_steps=[
                    f"Open {config_file}",
                    "Add or update the logging configuration:",
                    '  "logging": {',
                    '    "audit": true,',
                    '    "session": true,',
                    '    "level": "INFO"',
                    "  }",
                    "Ensure log files have proper permissions (600)",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html",
                ],
                fix_prompt=(
                    f"Enable audit logging in '{config_file.name}' by adding: "
                    f"'\"logging\": {{\"audit\": true, \"session\": true, \"level\": \"INFO\"}}'. "
                    f"This tracks all commands executed and helps detect unauthorized access. "
                    f"Set log file permissions to 600. Restart the service after changes."
                ),
            )
            self.findings.append(finding)

    def _check_pairing_codes(self, config: Dict[str, Any], config_file: Path) -> None:
        """Check for weak or default pairing codes."""
        pairing_code = None
        rate_limiting = None

        if "pairing" in config and isinstance(config["pairing"], dict):
            pairing_code = config["pairing"].get("code")
            rate_limiting = config["pairing"].get("rateLimit")

        if pairing_code is None and "security" in config:
            if isinstance(config["security"], dict):
                pairing_code = config["security"].get("pairingCode")

        # Check for weak/default pairing codes
        weak_codes = [
            "0000",
            "1234",
            "1111",
            "password",
            "admin",
            "default",
            "",
        ]

        if pairing_code and (
            pairing_code in weak_codes
            or len(str(pairing_code)) < 8
            or (str(pairing_code).isdigit() and len(str(pairing_code)) <= 6)
        ):
            finding = Finding(
                id="CLAWD-PAIR-001",
                title="Weak or Default Pairing Code",
                description=(
                    "Your Clawdbot uses a weak or default pairing code. Weak pairing "
                    "codes can be easily guessed or brute-forced, allowing unauthorized "
                    "devices to pair with your Clawdbot instance and gain full access."
                ),
                severity=Severity.HIGH,
                category=Category.AUTHENTICATION,
                cvss_score=8.0,
                evidence={
                    "config_file": str(config_file),
                    "code_length": (len(str(pairing_code)) if pairing_code else 0),
                    "is_numeric_only": (
                        str(pairing_code).isdigit() if pairing_code else None
                    ),
                },
                location=str(config_file),
                remediation=(
                    "Use a cryptographically secure random pairing code with rate limiting."
                ),
                remediation_steps=[
                    f"Open {config_file}",
                    "Generate a strong pairing code using a secure random generator",
                    "Example (Python): import secrets; print(secrets.token_urlsafe(16))",
                    "Update the pairing configuration:",
                    '  "pairing": {',
                    '    "code": "<your-secure-code>",',
                    '    "rateLimit": {',
                    '      "maxAttempts": 5,',
                    '      "windowSeconds": 300',
                    "    }",
                    "  }",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
                ],
                fix_prompt=(
                    f"Replace the weak pairing code in '{config_file.name}' with a strong random code. "
                    f"Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(16))\". "
                    f"Update config: '\"pairing\": {{\"code\": \"<new-secure-code>\", \"rateLimit\": "
                    f"{{\"maxAttempts\": 5, \"windowSeconds\": 300}}}}'. Restart the service."
                ),
            )
            self.findings.append(finding)

        # Check for missing rate limiting
        if pairing_code and not rate_limiting:
            finding = Finding(
                id="CLAWD-PAIR-002",
                title="No Rate Limiting on Pairing Attempts",
                description=(
                    "Your Clawdbot pairing configuration does not have rate limiting "
                    "enabled. Without rate limiting, attackers can attempt to guess "
                    "your pairing code through brute-force attacks without any delay."
                ),
                severity=Severity.MEDIUM,
                category=Category.AUTHENTICATION,
                cvss_score=5.5,
                evidence={
                    "config_file": str(config_file),
                    "rate_limiting": rate_limiting,
                },
                location=str(config_file),
                remediation=("Enable rate limiting on pairing attempts."),
                remediation_steps=[
                    f"Open {config_file}",
                    "Add rate limiting to the pairing configuration:",
                    '  "pairing": {',
                    '    "rateLimit": {',
                    '      "maxAttempts": 5,',
                    '      "windowSeconds": 300',
                    "    }",
                    "  }",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://cheatsheetseries.owasp.org/cheatsheets/Blocking_Brute_Force_Attacks.html",
                ],
                fix_prompt=(
                    f"Add rate limiting to pairing in '{config_file.name}': "
                    f"'\"pairing\": {{\"rateLimit\": {{\"maxAttempts\": 5, \"windowSeconds\": 300}}}}'. "
                    f"This limits failed attempts to 5 per 5 minutes, preventing brute-force attacks. "
                    f"Restart the service after changes."
                ),
            )
            self.findings.append(finding)

    def _check_prompt_injection_protection(
        self, config: Dict[str, Any], config_file: Path
    ) -> None:
        """Check for prompt injection protection settings."""
        untrusted_content_wrapped = None
        content_filtering = None

        if "security" in config and isinstance(config["security"], dict):
            untrusted_content_wrapped = config["security"].get("wrapUntrustedContent")
            content_filtering = config["security"].get("contentFiltering")

        if "prompt" in config and isinstance(config["prompt"], dict):
            # Only update if not already set from security section
            if untrusted_content_wrapped is None:
                untrusted_content_wrapped = config["prompt"].get("wrapUntrusted")
            if content_filtering is None:
                content_filtering = config["prompt"].get("filtering")

        if untrusted_content_wrapped is False or (
            untrusted_content_wrapped is None and content_filtering is None
        ):
            finding = Finding(
                id="CLAWD-PROMPT-001",
                title="Prompt Injection Protection Not Configured",
                description=(
                    "Your Clawdbot does not have prompt injection protection configured. "
                    "When processing web content or external data, malicious prompts can "
                    "be injected that cause the AI to perform unintended actions. Untrusted "
                    "content should be wrapped in special tags to prevent injection attacks."
                ),
                severity=Severity.HIGH,
                category=Category.PROMPT_INJECTION,
                cvss_score=7.5,
                evidence={
                    "config_file": str(config_file),
                    "wrap_untrusted_content": untrusted_content_wrapped,
                    "content_filtering": content_filtering,
                },
                location=str(config_file),
                remediation=(
                    "Enable prompt injection protection by wrapping untrusted content."
                ),
                remediation_steps=[
                    f"Open {config_file}",
                    "Add prompt injection protection settings:",
                    '  "security": {',
                    '    "wrapUntrustedContent": true,',
                    '    "contentFiltering": "strict"',
                    "  }",
                    "This will automatically wrap web content in <untrusted> tags",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://simonwillison.net/2023/Apr/14/worst-that-can-happen/",
                    "https://owasp.org/www-project-top-10-for-large-language-model-applications/",
                ],
                fix_prompt=(
                    f"Enable prompt injection protection in '{config_file.name}' by adding: "
                    f"'\"security\": {{\"wrapUntrustedContent\": true, \"contentFiltering\": \"strict\"}}'. "
                    f"This automatically wraps external content in <untrusted> tags to prevent "
                    f"malicious prompt injection. Restart the service after changes."
                ),
            )
            self.findings.append(finding)
