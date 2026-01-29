"""
File Permission Checker Module

This module checks file permissions for sensitive configuration files.
"""

import stat
from pathlib import Path
from typing import List

from clawd_for_dummies.models.finding import Finding, Severity, Category
from clawd_for_dummies.models.system_info import SystemInfo
from clawd_for_dummies.engine.base_scanner import BaseScanner


class FilePermissionChecker(BaseScanner):
    """
    Scanner for checking file permissions on sensitive files.

    This scanner checks for:
    - World-readable config files
    - World-writable config files
    - Backup files with sensitive data
    - Incorrect ownership
    """

    def __init__(self, system_info: SystemInfo, verbose: bool = False):
        """Initialize the file permission checker."""
        super().__init__(system_info, verbose)
        self.findings: List[Finding] = []

    @classmethod
    def get_name(cls) -> str:
        """Get scanner name."""
        return "File Permission Checker"

    @classmethod
    def get_description(cls) -> str:
        """Get scanner description."""
        return "Validates file permissions on sensitive configuration files"

    def scan(self) -> List[Finding]:
        """
        Perform file permission security scan.

        Returns:
            List of security findings
        """
        self.findings = []

        self.log("Checking file permissions...")

        # Find sensitive files
        sensitive_files = self._find_sensitive_files()

        for file_path in sensitive_files:
            self._check_file_permissions(file_path)

        # Check for backup files
        self._check_backup_files()

        return self.findings

    def _find_sensitive_files(self) -> List[Path]:
        """Find sensitive configuration files."""
        files = []
        home = Path(self.system_info.home_directory)

        # Moltbot/Clawdbot specific file patterns
        patterns = [
            "moltbot.json",
            "clawdbot.json",
            "settings.json",
            ".env",
            ".env.local",
            "secrets.json",
            "credentials.json",
            "*.key",
            "*.pem",
        ]

        # Check Moltbot and Clawdbot locations only
        # Note: Claude Desktop paths are NOT scanned as they are for
        # the Claude Desktop App, not Moltbot/Clawdbot
        # Note: Current directory (.) and config/ are NOT scanned to avoid
        # false positives from non-Moltbot/Clawdbot configuration files
        locations = [
            home / ".config" / "moltbot",
            home / ".config" / "clawdbot",
            home / ".moltbot",
            home / ".clawdbot",
            home / "Library" / "Application Support" / "Moltbot",
            home / "Library" / "Application Support" / "Clawdbot",
        ]

        for location in locations:
            if location.exists():
                for pattern in patterns:
                    if "*" in pattern:
                        files.extend(location.glob(pattern))
                    else:
                        file_path = location / pattern
                        if file_path.exists():
                            files.append(file_path)

        return list(set(files))  # Remove duplicates

    def _check_file_permissions(self, file_path: Path) -> None:
        """Check permissions on a single file."""
        try:
            file_stat = file_path.stat()
            mode = file_stat.st_mode

            # Check if world-readable
            if mode & stat.S_IROTH:
                self._add_world_readable_finding(file_path, mode)

            # Check if world-writable
            if mode & stat.S_IWOTH:
                self._add_world_writable_finding(file_path, mode)

            # Check if group-writable (less critical but still worth noting)
            if mode & stat.S_IWGRP:
                self._add_group_writable_finding(file_path, mode)

        except Exception as e:
            self.log(f"Error checking {file_path}: {e}")

    def _check_backup_files(self) -> None:
        """Check for backup files that might contain sensitive data."""
        home = Path(self.system_info.home_directory)

        # Backup file extensions
        backup_extensions = [".bak", ".backup", ".old", ".orig", "~"]

        # Check Moltbot and Clawdbot locations only
        # Note: Claude Desktop paths are NOT scanned as they are for
        # the Claude Desktop App, not Moltbot/Clawdbot
        # Note: Current directory (.) is NOT scanned to avoid false positives
        locations = [
            home / ".config" / "moltbot",
            home / ".config" / "clawdbot",
            home / ".moltbot",
            home / ".clawdbot",
        ]

        for location in locations:
            if location.exists():
                for ext in backup_extensions:
                    for backup_file in location.glob(f"*{ext}"):
                        if backup_file.is_file():
                            self._add_backup_file_finding(backup_file)

    def _add_world_readable_finding(self, file_path: Path, mode: int) -> None:
        """Add a finding for world-readable file."""
        # Convert mode to octal string for display
        mode_str = oct(mode)[-3:]

        finding = Finding(
            id="CLAWD-PERM-001",
            title=f"World-Readable Configuration File: {file_path.name}",
            description=(
                f"The file '{file_path.name}' is readable by any user on the system "
                f"(permissions: {mode_str}). This means other users can read your "
                f"configuration and potentially extract sensitive information like API keys."
            ),
            severity=Severity.MEDIUM,
            category=Category.PERMISSION,
            cvss_score=5.0,
            evidence={
                "file": str(file_path),
                "permissions": mode_str,
            },
            location=str(file_path),
            remediation=(
                "Change file permissions to restrict access to only the owner."
            ),
            remediation_steps=[
                f"Run: chmod 600 {file_path}",
                "Or on Windows: Right-click > Properties > Security > Restrict access",
                (
                    "Verify: ls -la {file_path}"
                    if not self.system_info.is_windows
                    else ""
                ),
            ],
            reference_links=[
                "https://chmod-calculator.com/",
            ],
            fix_prompt=(
                f"Restrict file permissions on '{file_path}' to owner-only access. "
                f"Run 'chmod 600 {file_path}' on Unix/Linux/macOS to set read-write for owner only. "
                f"On Windows, right-click the file > Properties > Security tab > Edit, and remove "
                f"read permissions for 'Everyone' and other non-owner groups."
            ),
        )
        self.findings.append(finding)

    def _add_world_writable_finding(self, file_path: Path, mode: int) -> None:
        """Add a finding for world-writable file."""
        mode_str = oct(mode)[-3:]

        finding = Finding(
            id="CLAWD-PERM-002",
            title=f"World-Writable Configuration File: {file_path.name}",
            description=(
                f"The file '{file_path.name}' is writable by any user on the system "
                f"(permissions: {mode_str}). This allows any user to modify your "
                f"configuration, potentially injecting malicious settings or backdoors."
            ),
            severity=Severity.HIGH,
            category=Category.PERMISSION,
            cvss_score=7.5,
            evidence={
                "file": str(file_path),
                "permissions": mode_str,
            },
            location=str(file_path),
            remediation=(
                "Change file permissions to restrict write access to only the owner."
            ),
            remediation_steps=[
                f"Run: chmod 600 {file_path}",
                "Verify the file is not writable by group or others",
                "Check for signs of tampering in the file contents",
            ],
            reference_links=[
                "https://chmod-calculator.com/",
            ],
            fix_prompt=(
                f"Remove world-write permissions from '{file_path}' immediately. "
                f"Run 'chmod 600 {file_path}' on Unix/Linux/macOS. Review the file contents "
                f"for any signs of tampering or malicious modifications. If the file appears "
                f"compromised, restore from a known-good backup and rotate any credentials it contains."
            ),
        )
        self.findings.append(finding)

    def _add_group_writable_finding(self, file_path: Path, mode: int) -> None:
        """Add a finding for group-writable file."""
        mode_str = oct(mode)[-3:]

        finding = Finding(
            id="CLAWD-PERM-003",
            title=f"Group-Writable Configuration File: {file_path.name}",
            description=(
                f"The file '{file_path.name}' is writable by its group "
                f"(permissions: {mode_str}). If multiple users are in the same group, "
                f"they could modify this file."
            ),
            severity=Severity.LOW,
            category=Category.PERMISSION,
            cvss_score=3.0,
            evidence={
                "file": str(file_path),
                "permissions": mode_str,
            },
            location=str(file_path),
            remediation=("Remove group write permissions if not needed."),
            remediation_steps=[
                f"Run: chmod g-w {file_path}",
                "Or: chmod 600 {file_path} to restrict to owner only",
            ],
            reference_links=[
                "https://chmod-calculator.com/",
            ],
            fix_prompt=(
                f"Remove group write permissions from '{file_path}'. "
                f"Run 'chmod g-w {file_path}' to remove just group write access, or "
                f"'chmod 600 {file_path}' to restrict all access to owner only. "
                f"Verify with 'ls -la {file_path}' that permissions are correctly set."
            ),
        )
        self.findings.append(finding)

    def _add_backup_file_finding(self, backup_file: Path) -> None:
        """Add a finding for backup file."""
        finding = Finding(
            id="CLAWD-PERM-004",
            title=f"Backup File Found: {backup_file.name}",
            description=(
                f"A backup file '{backup_file.name}' was found. Backup files often "
                f"contain the same sensitive information as the original file but are "
                f"forgotten and left unprotected."
            ),
            severity=Severity.LOW,
            category=Category.PERMISSION,
            cvss_score=2.0,
            evidence={
                "file": str(backup_file),
            },
            location=str(backup_file),
            remediation=("Remove backup files or secure them properly."),
            remediation_steps=[
                f"Review the contents of {backup_file}",
                "If it contains sensitive data, either:",
                "  - Delete it if no longer needed",
                "  - Move it to a secure, encrypted location",
                "  - Set restrictive permissions (chmod 600)",
            ],
            reference_links=[
                "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
            ],
            fix_prompt=(
                f"Review and secure the backup file '{backup_file}'. If the file is no longer "
                f"needed, securely delete it with 'shred -u {backup_file}' (Linux) or a secure "
                f"delete tool. If needed, move it to encrypted storage and set permissions to "
                f"'chmod 600 {backup_file}'. Never leave backup files with sensitive data unprotected."
            ),
        )
        self.findings.append(finding)
