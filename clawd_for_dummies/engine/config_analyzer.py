"""
Configuration Analyzer Module

This module analyzes Clawdbot configuration files for security issues.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from clawd_for_dummies.models.finding import Finding, Severity, Category
from clawd_for_dummies.models.system_info import SystemInfo
from clawd_for_dummies.engine.base_scanner import BaseScanner


class ConfigAnalyzer(BaseScanner):
    """
    Scanner for analyzing Clawdbot configuration files.

    This scanner checks for:
    - Missing security settings
    - Overly permissive configurations
    - Insecure defaults
    - Missing authentication
    """

    def __init__(self, system_info: SystemInfo, verbose: bool = False):
        """Initialize the config analyzer."""
        super().__init__(system_info, verbose)
        self.findings: List[Finding] = []

    @classmethod
    def get_name(cls) -> str:
        """Get scanner name."""
        return "Config Analyzer"

    @classmethod
    def get_description(cls) -> str:
        """Get scanner description."""
        return "Validates Clawdbot configuration files for security issues"

    def scan(self) -> List[Finding]:
        """
        Perform configuration security scan.

        Returns:
            List of security findings
        """
        self.findings = []

        self.log("Analyzing configuration files...")

        # Find and analyze config files
        config_files = self._find_config_files()

        for config_file in config_files:
            self._analyze_config_file(config_file)

        if not config_files:
            self.log("No Clawdbot configuration files found")

        return self.findings

    def _find_config_files(self) -> List[Path]:
        """Find Clawdbot configuration files."""
        config_files = []
        home = Path(self.system_info.home_directory)

        # Platform-specific paths for Moltbot and Clawdbot only
        # Note: Claude Desktop paths are NOT scanned as they are for
        # the Claude Desktop App, not Moltbot/Clawdbot
        if self.system_info.is_windows:
            appdata = home / "AppData" / "Roaming"
            localappdata = home / "AppData" / "Local"
            paths = [
                appdata / "Moltbot" / "settings.json",
                appdata / "Clawdbot" / "settings.json",
                localappdata / "Moltbot" / "settings.json",
                localappdata / "Clawdbot" / "settings.json",
            ]
        elif self.system_info.is_macos:
            paths = [
                home / "Library" / "Application Support" / "Moltbot" / "settings.json",
                home / "Library" / "Application Support" / "Clawdbot" / "settings.json",
            ]
        else:  # Linux
            paths = [
                home / ".config" / "moltbot" / "settings.json",
                home / ".config" / "clawdbot" / "settings.json",
                home / ".moltbot" / "settings.json",
                home / ".clawdbot" / "settings.json",
            ]

        # Common Moltbot/Clawdbot files in home directory and current working directory
        paths.extend(
            [
                home / "moltbot.json",
                home / "clawdbot.json",
                Path("moltbot.json"),
                Path("clawdbot.json"),
            ]
        )

        for path in paths:
            if path.exists():
                config_files.append(path)

        return config_files

    def _analyze_config_file(self, config_file: Path) -> None:
        """Analyze a single configuration file."""
        self.log(f"Analyzing {config_file}...")

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Check for security settings
            self._check_authentication(config, config_file)
            self._check_cors_settings(config, config_file)
            self._check_allowed_origins(config, config_file)
            self._check_logging(config, config_file)
            self._check_gateway_settings(config, config_file)

        except json.JSONDecodeError:
            self.log(f"Invalid JSON in {config_file}")
        except Exception as e:
            self.log(f"Error analyzing {config_file}: {e}")

    def _check_authentication(self, config: Dict[str, Any], config_file: Path) -> None:
        """Check if authentication is enabled."""
        # Check various possible locations for auth setting
        auth_enabled = None

        # Check in 'security' section
        if "security" in config and isinstance(config["security"], dict):
            auth_enabled = config["security"].get("requireAuthentication")

        # Check in 'gateway' section
        if auth_enabled is None and "gateway" in config:
            gateway = config["gateway"]
            if isinstance(gateway, dict):
                auth_enabled = gateway.get("requireAuthentication")

        # Check top-level
        if auth_enabled is None:
            auth_enabled = config.get("requireAuthentication")

        # Check for auth token/password presence
        has_auth_token = (
            config.get("authToken") is not None
            or config.get("password") is not None
            or (
                isinstance(config.get("security"), dict)
                and config["security"].get("authToken")
            )
        )

        if auth_enabled is False or (auth_enabled is None and not has_auth_token):
            finding = Finding(
                id="CLAWD-CONFIG-001",
                title="Authentication Not Enabled",
                description=(
                    "Your Clawdbot configuration does not have authentication enabled. "
                    "This means anyone who can connect to your gateway can control your "
                    "Clawdbot instance without providing any credentials."
                ),
                severity=Severity.HIGH,
                category=Category.AUTHENTICATION,
                cvss_score=8.0,
                evidence={
                    "config_file": str(config_file),
                    "require_authentication": auth_enabled,
                    "has_auth_token": has_auth_token,
                },
                location=str(config_file),
                remediation=(
                    "Enable authentication in your Clawdbot configuration file."
                ),
                remediation_steps=[
                    f"Open {config_file}",
                    "Add or set 'requireAuthentication' to true",
                    "Set a strong password or auth token",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://github.com/jasondsmith72/Clawdbot",
                ],
                fix_prompt=(
                    f"Enable authentication in '{config_file.name}' by adding "
                    f"'\"requireAuthentication\": true' and setting a strong "
                    f"'\"authToken\": \"<random-32-char-string>\"' in the configuration. "
                    f"Generate a secure token using: python -c \"import secrets; print(secrets.token_urlsafe(32))\". "
                    f"Restart the Moltbot/Clawdbot service after making changes."
                ),
            )
            self.findings.append(finding)

    def _check_cors_settings(self, config: Dict[str, Any], config_file: Path) -> None:
        """Check CORS settings."""
        cors_enabled = None

        if "security" in config and isinstance(config["security"], dict):
            cors_enabled = config["security"].get("enableCORS")

        if cors_enabled is None:
            cors_enabled = config.get("enableCORS")

        if cors_enabled is True:
            finding = Finding(
                id="CLAWD-CONFIG-002",
                title="CORS Enabled Without Restrictions",
                description=(
                    "Cross-Origin Resource Sharing (CORS) is enabled in your configuration. "
                    "This allows web pages from other domains to interact with your Clawdbot "
                    "instance, which could be exploited by malicious websites."
                ),
                severity=Severity.MEDIUM,
                category=Category.CONFIG,
                cvss_score=5.0,
                evidence={
                    "config_file": str(config_file),
                    "enable_cors": cors_enabled,
                },
                location=str(config_file),
                remediation=(
                    "Disable CORS or restrict it to specific trusted origins."
                ),
                remediation_steps=[
                    f"Open {config_file}",
                    "Set 'enableCORS' to false, or",
                    "Configure 'allowedOrigins' to only trusted domains",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS",
                ],
                fix_prompt=(
                    f"Disable unrestricted CORS in '{config_file.name}' by either setting "
                    f"'\"enableCORS\": false' or restricting allowed origins with "
                    f"'\"allowedOrigins\": [\"https://trusted-domain.com\"]'. Only whitelist "
                    f"domains you explicitly trust. Restart the service after changes."
                ),
            )
            self.findings.append(finding)

    def _check_allowed_origins(self, config: Dict[str, Any], config_file: Path) -> None:
        """Check allowed origins configuration."""
        allowed_origins = None

        if "security" in config and isinstance(config["security"], dict):
            allowed_origins = config["security"].get("allowedOrigins")

        if allowed_origins is None:
            allowed_origins = config.get("allowedOrigins")

        if allowed_origins == "*" or (
            isinstance(allowed_origins, list) and "*" in allowed_origins
        ):
            finding = Finding(
                id="CLAWD-CONFIG-003",
                title="Allowed Origins Set to Wildcard",
                description=(
                    "Your configuration allows connections from ANY origin (domain). "
                    "This means any website can attempt to connect to your Clawdbot instance."
                ),
                severity=Severity.HIGH,
                category=Category.CONFIG,
                cvss_score=7.0,
                evidence={
                    "config_file": str(config_file),
                    "allowed_origins": allowed_origins,
                },
                location=str(config_file),
                remediation=("Specify only trusted domains in allowedOrigins."),
                remediation_steps=[
                    f"Open {config_file}",
                    "Replace '*' with specific trusted domains",
                    'Example: ["https://localhost:3000", "https://myapp.com"]',
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin",
                ],
                fix_prompt=(
                    f"Replace the wildcard '*' in allowedOrigins in '{config_file.name}' with "
                    f"a specific list of trusted domains. Use format: "
                    f"'\"allowedOrigins\": [\"https://localhost:3000\", \"https://your-app.com\"]'. "
                    f"Only include domains you control and trust. Restart the service after changes."
                ),
            )
            self.findings.append(finding)

    def _check_logging(self, config: Dict[str, Any], config_file: Path) -> None:
        """Check logging configuration."""
        log_level = None

        if "logging" in config and isinstance(config["logging"], dict):
            log_level = config["logging"].get("level")

        if log_level is None:
            log_level = config.get("logLevel")

        # Check if logging might expose sensitive data
        if log_level and log_level.upper() in ["DEBUG", "TRACE"]:
            finding = Finding(
                id="CLAWD-CONFIG-004",
                title="Verbose Logging May Expose Sensitive Data",
                description=(
                    f"Your configuration has logging set to '{log_level}'. "
                    "Verbose logging can capture sensitive information like API keys, "
                    "tokens, and user data in log files."
                ),
                severity=Severity.LOW,
                category=Category.LOGGING,
                cvss_score=3.0,
                evidence={
                    "config_file": str(config_file),
                    "log_level": log_level,
                },
                location=str(config_file),
                remediation=("Set log level to 'INFO' or 'WARNING' in production."),
                remediation_steps=[
                    f"Open {config_file}",
                    "Change 'logLevel' to 'INFO' or 'WARNING'",
                    "Clear existing log files that may contain sensitive data",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html",
                ],
                fix_prompt=(
                    f"Change the log level in '{config_file.name}' from '{log_level}' to 'INFO' "
                    f"or 'WARNING' for production use. Set '\"logLevel\": \"INFO\"' in the config. "
                    f"After changing, securely delete existing log files that may contain sensitive "
                    f"data using 'shred -u' (Linux) or secure delete tools. Restart the service."
                ),
            )
            self.findings.append(finding)

    def _check_gateway_settings(
        self, config: Dict[str, Any], config_file: Path
    ) -> None:
        """Check gateway binding settings."""
        bind_address = None

        if "gateway" in config and isinstance(config["gateway"], dict):
            bind_address = config["gateway"].get("bind")

        if bind_address is None:
            bind_address = config.get("bind")

        if bind_address == "0.0.0.0":
            finding = Finding(
                id="CLAWD-CONFIG-005",
                title="Gateway Bound to All Network Interfaces",
                description=(
                    "Your Clawdbot gateway is configured to listen on all network "
                    "interfaces (0.0.0.0). This makes it accessible from any computer "
                    "on your network or the internet."
                ),
                severity=Severity.CRITICAL,
                category=Category.CONFIG,
                cvss_score=9.0,
                evidence={
                    "config_file": str(config_file),
                    "bind_address": bind_address,
                },
                location=str(config_file),
                remediation=("Change the bind address to localhost only (127.0.0.1)."),
                remediation_steps=[
                    f"Open {config_file}",
                    "Find the 'gateway' or 'bind' setting",
                    "Change 'bind' from '0.0.0.0' to '127.0.0.1'",
                    "Restart Moltbot/Clawdbot to apply changes",
                ],
                reference_links=[
                    "https://github.com/jasondsmith72/Clawdbot",
                ],
                fix_prompt=(
                    f"Change the gateway bind address in '{config_file.name}' from '0.0.0.0' to "
                    f"'127.0.0.1' to prevent network exposure. Update the setting to "
                    f"'\"gateway\": {{\"bind\": \"127.0.0.1\"}}' or '\"bind\": \"127.0.0.1\"'. "
                    f"This restricts access to localhost only. Restart the service after changes."
                ),
            )
            self.findings.append(finding)
