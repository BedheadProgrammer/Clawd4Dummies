"""
Credential scanner for detecting exposed API keys and secrets.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Pattern, Set, Tuple

from clawd_for_dummies.models.finding import Finding, Severity, Category
from clawd_for_dummies.models.system_info import SystemInfo
from clawd_for_dummies.engine.base_scanner import BaseScanner


class CredentialScanner(BaseScanner):
    """Scans for exposed API keys, tokens, and credentials."""

    CREDENTIAL_PATTERNS: Dict[str, Tuple[Pattern, str, Severity]] = {
        "anthropic_api_key": (
            re.compile(r"sk-ant-api03-[a-zA-Z0-9_-]{40,}", re.IGNORECASE),
            "Anthropic API Key",
            Severity.CRITICAL,
        ),
        "openai_api_key": (
            re.compile(r"sk-(?:proj-[a-zA-Z0-9_-]+|[a-zA-Z0-9]{48})", re.IGNORECASE),
            "OpenAI API Key",
            Severity.CRITICAL,
        ),
        "slack_bot_token": (
            re.compile(r"xox[baprs]-[0-9a-zA-Z-]{10,48}", re.IGNORECASE),
            "Slack Bot Token",
            Severity.HIGH,
        ),
        "slack_webhook": (
            re.compile(r"https://hooks\.slack\.com/services/[A-Z0-9/]+", re.IGNORECASE),
            "Slack Webhook URL",
            Severity.HIGH,
        ),
        "discord_bot_token": (
            re.compile(r"[MN][A-Za-z\d]{23}\.[A-Za-z\d]{6}\.[A-Za-z\d]{27}"),
            "Discord Bot Token",
            Severity.HIGH,
        ),
        "discord_webhook": (
            re.compile(
                r"https://discord(?:app)?\.com/api/webhooks/[0-9]+/[a-zA-Z0-9_-]+",
                re.IGNORECASE,
            ),
            "Discord Webhook URL",
            Severity.HIGH,
        ),
        "telegram_bot_token": (
            re.compile(r"[0-9]+:[a-zA-Z0-9_-]{35}", re.IGNORECASE),
            "Telegram Bot Token",
            Severity.HIGH,
        ),
        "aws_access_key": (
            re.compile(r"AKIA[0-9A-Z]{16}", re.IGNORECASE),
            "AWS Access Key ID",
            Severity.CRITICAL,
        ),
        "aws_secret_key": (
            re.compile(
                r"(?:aws_secret_access_key|secret_access_key|aws_secret_key)"
                r"[\"\s]*[:=][\"\s]*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
                re.IGNORECASE,
            ),
            "AWS Secret Key",
            Severity.CRITICAL,
        ),
        "github_token": (
            re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}", re.IGNORECASE),
            "GitHub Personal Access Token",
            Severity.CRITICAL,
        ),
        "google_api_key": (
            re.compile(r"AIza[0-9A-Za-z_-]{35}", re.IGNORECASE),
            "Google API Key",
            Severity.HIGH,
        ),
        "stripe_key": (
            re.compile(r"sk_(?:live|test)_[0-9a-zA-Z]{24,}", re.IGNORECASE),
            "Stripe Secret Key",
            Severity.CRITICAL,
        ),
        "database_password": (
            re.compile(
                r"(mongodb|mysql|postgres|postgresql)://[^:]+:([^@]+)@",
                re.IGNORECASE,
            ),
            "Database Password in Connection String",
            Severity.CRITICAL,
        ),
        "generic_api_key": (
            re.compile(
                r"api[_-]?key[\"\s]*[:=][\"\s]*[a-zA-Z0-9_\-]{16,}",
                re.IGNORECASE,
            ),
            "Generic API Key",
            Severity.MEDIUM,
        ),
        "generic_secret": (
            re.compile(r"secret[\"\s]*[:=][\"\s]*[a-zA-Z0-9_\-]{8,}", re.IGNORECASE),
            "Generic Secret",
            Severity.MEDIUM,
        ),
        "password_in_config": (
            re.compile(r"password[\"\s]*[:=][\"\s]*[^\s\"]+", re.IGNORECASE),
            "Password in Configuration",
            Severity.HIGH,
        ),
    }

    CONFIG_PATHS: List[Tuple[str, List[str]]] = [
        (
            ".",
            [
                "*.json",
                "*.yaml",
                "*.yml",
                "*.env",
                "*.conf",
                "*.config",
                "*.txt",
            ],
        ),
        ("config", ["*"]),
        (".config", ["*"]),
    ]

    SPECIFIC_FILES: List[str] = [
        "moltbot.json",
        "clawdbot.json",
        "settings.json",
        ".env",
        ".env.local",
        ".env.production",
        "config.json",
        "secrets.json",
        "credentials.json",
    ]

    # Files to exclude from credential scanning (contain hashes, not credentials)
    EXCLUDED_FILES: List[str] = [
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "Cargo.lock",
        "poetry.lock",
        "Pipfile.lock",
        "composer.lock",
        "Gemfile.lock",
        "go.sum",
        "pubspec.lock",
    ]

    def __init__(self, system_info: SystemInfo, verbose: bool = False):
        super().__init__(system_info, verbose)
        self.findings: List[Finding] = []

    @classmethod
    def get_name(cls) -> str:
        return "Credential Scanner"

    @classmethod
    def get_description(cls) -> str:
        return "Scans for exposed API keys, tokens, and credentials"

    def scan(self) -> List[Finding]:
        self.findings = []
        self.log("Scanning for exposed credentials...")

        self._scan_environment_variables()
        self._scan_config_files()
        self._scan_specific_files()

        return self.findings

    def _scan_environment_variables(self) -> None:
        self.log("Checking environment variables...")

        sensitive_vars = [
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY",
            "SLACK_BOT_TOKEN",
            "SLACK_WEBHOOK_URL",
            "DISCORD_BOT_TOKEN",
            "DISCORD_WEBHOOK_URL",
            "TELEGRAM_BOT_TOKEN",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "GITHUB_TOKEN",
            "GOOGLE_API_KEY",
            "STRIPE_SECRET_KEY",
            "DATABASE_URL",
            "DB_PASSWORD",
            "PASSWORD",
            "SECRET_KEY",
            "API_KEY",
        ]

        for var_name in sensitive_vars:
            value = os.environ.get(var_name)
            if value:
                if len(value) > 8 and not value.startswith("${"):
                    self._add_env_credential_finding(var_name, value)

    def _scan_config_files(self) -> None:
        self.log("Scanning configuration files...")

        home = Path(self.system_info.home_directory)

        # Scan Moltbot and Clawdbot directories for credentials
        # Note: Claude Desktop paths are NOT scanned as they are for
        # the Claude Desktop App, not Moltbot/Clawdbot
        # Note: Current directory (.) and config/ are NOT scanned to avoid
        # false positives from non-Moltbot/Clawdbot configuration files
        config_dirs = [
            home / ".config" / "moltbot",
            home / ".config" / "clawdbot",
            home / ".moltbot",
            home / ".clawdbot",
        ]

        for config_dir in config_dirs:
            if config_dir.exists():
                self._scan_directory(config_dir)

    def _scan_directory(self, directory: Path) -> None:
        try:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    if file_path.suffix.lower() in [
                        ".json",
                        ".yaml",
                        ".yml",
                        ".env",
                        ".conf",
                        ".txt",
                    ]:
                        self._scan_file(file_path)
                elif file_path.is_dir() and not file_path.name.startswith("."):
                    if len(file_path.parts) - len(directory.parts) < 3:
                        self._scan_directory(file_path)
        except PermissionError:
            self.log(f"Permission denied: {directory}")
        except Exception as e:
            self.log(f"Error scanning {directory}: {e}")

    def _scan_specific_files(self) -> None:
        home = Path(self.system_info.home_directory)

        # Scan Moltbot and Clawdbot config files for credentials
        # Note: Claude Desktop paths are NOT scanned as they are for
        # the Claude Desktop App, not Moltbot/Clawdbot
        if self.system_info.is_windows:
            appdata = os.environ.get("APPDATA", "")
            localappdata = os.environ.get("LOCALAPPDATA", "")
            paths = []
            if appdata:
                paths.extend([
                    Path(appdata) / "Moltbot" / "settings.json",
                    Path(appdata) / "Clawdbot" / "settings.json",
                ])
            if localappdata:
                paths.extend([
                    Path(localappdata) / "Moltbot" / "settings.json",
                    Path(localappdata) / "Clawdbot" / "settings.json",
                ])
        elif self.system_info.is_macos:
            paths = [
                home / "Library" / "Application Support" / "Moltbot" / "settings.json",
                home / "Library" / "Application Support" / "Clawdbot" / "settings.json",
            ]
        else:
            paths = [
                home / ".config" / "moltbot" / "settings.json",
                home / ".config" / "clawdbot" / "settings.json",
                home / ".moltbot" / "settings.json",
                home / ".clawdbot" / "settings.json",
            ]

        paths.extend(
            [
                home / "moltbot.json",
                home / "clawdbot.json",
                Path("moltbot.json"),
                Path("clawdbot.json"),
            ]
        )

        for file_path in paths:
            if file_path.exists():
                self._scan_file(file_path)

    def _scan_file(self, file_path: Path) -> None:
        try:
            # Skip excluded files (lock files that contain hashes, not credentials)
            if file_path.name in self.EXCLUDED_FILES:
                return

            if file_path.stat().st_size > 10 * 1024 * 1024:
                return

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Track which pattern types we've already reported for this file
            # to avoid duplicate findings for the same file and pattern
            reported_patterns: Set[str] = set()

            for pattern_name, (
                pattern,
                credential_type,
                severity,
            ) in self.CREDENTIAL_PATTERNS.items():
                match = pattern.search(content)

                if match and pattern_name not in reported_patterns:
                    # Mark this pattern as reported for this file
                    reported_patterns.add(pattern_name)

                    # Use capturing group if available, otherwise use full match
                    try:
                        credential = match.group(1)
                    except IndexError:
                        credential = match.group(0)
                    masked = self._mask_credential(credential)

                    self._add_file_credential_finding(
                        file_path=file_path,
                        credential_type=credential_type,
                        pattern_name=pattern_name,
                        matched_text=masked,
                        severity=severity,
                    )

        except PermissionError:
            self.log(f"Permission denied: {file_path}")
        except Exception as e:
            self.log(f"Error reading {file_path}: {e}")

    def _mask_credential(self, credential: str) -> str:
        if len(credential) <= 8:
            return "*" * len(credential)

        visible_chars = 4
        return (
            credential[:visible_chars]
            + "*" * (len(credential) - visible_chars * 2)
            + credential[-visible_chars:]
        )

    def _add_env_credential_finding(self, var_name: str, value: str) -> None:
        masked_value = self._mask_credential(value)

        finding = Finding(
            id=f"CLAWD-CRED-ENV-{var_name}",
            title=f"{var_name} Exposed in Environment",
            description=(
                f"The environment variable '{var_name}' contains what appears "
                f"to be a sensitive credential. Environment variables can be "
                f"accessed by any process running as the same user, and may "
                f"be logged by various system tools."
            ),
            severity=Severity.HIGH,
            category=Category.CREDENTIAL,
            cvss_score=7.5,
            evidence={
                "variable": var_name,
                "value_preview": masked_value,
            },
            location=f"Environment variable: {var_name}",
            remediation=(
                "Move the credential to a secure secrets manager or "
                "encrypted configuration file with restricted permissions."
            ),
            remediation_steps=[
                "Remove the credential from environment variables",
                "Use a secrets manager (e.g., 1Password, Bitwarden, AWS Secrets Manager)",
                "Or store in an encrypted file with 600 permissions",
                "Update your application to read from the secure location",
            ],
            reference_links=[
                "https://12factor.net/config",
                "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
            ],
            fix_prompt=(
                f"Remove the '{var_name}' credential from environment variables and move it "
                f"to a secure secrets manager. Unset the environment variable with "
                f"'unset {var_name}' (Unix) or remove it from System Properties (Windows). "
                f"Store the credential in a secrets manager like 1Password, Bitwarden, or "
                f"AWS Secrets Manager, and update the application to retrieve it securely."
            ),
        )

        self.findings.append(finding)

    def _add_file_credential_finding(
        self,
        file_path: Path,
        credential_type: str,
        pattern_name: str,
        matched_text: str,
        severity: Severity,
    ) -> None:
        finding = Finding(
            id=f"CLAWD-CRED-FILE-{pattern_name}",
            title=f"{credential_type} Found in Configuration File",
            description=(
                f"A {credential_type} was found in the file '{file_path.name}'. "
                f"Storing credentials in plain text files is a serious security risk. "
                f"Anyone with access to this file can steal and misuse the credential."
            ),
            severity=severity,
            category=Category.CREDENTIAL,
            cvss_score=9.0 if severity == Severity.CRITICAL else 7.5,
            evidence={
                "file": str(file_path),
                "credential_type": credential_type,
                "matched_text": matched_text,
            },
            location=str(file_path),
            remediation=(
                f"Remove the {credential_type} from this file immediately. "
                f"Use environment variables or a secure secrets manager instead."
            ),
            remediation_steps=[
                f"Remove the {credential_type} from {file_path.name}",
                "Revoke the exposed credential immediately",
                "Generate a new credential",
                "Store the new credential in a secure location",
                "Update your application to use the secure storage",
                "Check logs and access history for unauthorized use",
            ],
            reference_links=[
                "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
                "https://docs.github.com/en/code-security/secret-scanning",
            ],
            fix_prompt=(
                f"Remove the exposed {credential_type} from '{file_path.name}' immediately. "
                f"First, revoke the compromised credential at its source (e.g., regenerate the API key). "
                f"Then delete the credential from the file and replace it with a reference to a "
                f"secure secrets manager or environment variable. Set file permissions to 600 "
                f"(chmod 600 {file_path.name}) to restrict access."
            ),
        )

        self.findings.append(finding)
