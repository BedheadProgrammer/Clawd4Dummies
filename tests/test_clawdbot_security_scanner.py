"""
Tests for the Clawdbot Security Scanner.
"""

import json
import pytest
import tempfile
from pathlib import Path

from clawd_for_dummies.engine.clawdbot_security_scanner import (
    ClawdbotSecurityScanner,
)
from clawd_for_dummies.models.system_info import SystemInfo
from clawd_for_dummies.models.finding import Severity, Category


class TestClawdbotSecurityScanner:
    """Tests for the ClawdbotSecurityScanner module."""

    @pytest.fixture
    def system_info(self):
        """Create a mock system info object."""
        return SystemInfo(
            hostname="test-host",
            os_name="Linux",
            python_version="3.9.0",
        )

    @pytest.fixture
    def scanner(self, system_info):
        """Create a scanner instance."""
        return ClawdbotSecurityScanner(system_info, verbose=False)

    def test_scanner_name(self, scanner):
        """Test scanner name."""
        assert scanner.get_name() == "Clawdbot/Moltbot Security Scanner"

    def test_scanner_description(self, scanner):
        """Test scanner description."""
        description = scanner.get_description()
        assert "Clawdbot/Moltbot" in description

    def test_dm_policy_all_users(self, system_info):
        """Test detection of permissive DM policy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "claude_desktop_config.json"
            config = {"dm": {"policy": "all"}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            scanner.analyze_config_file(config_file)

            assert len(scanner.findings) >= 1
            dm_findings = [f for f in scanner.findings if f.id == "CLAWD-DM-001"]
            assert len(dm_findings) == 1
            assert dm_findings[0].severity == Severity.HIGH
            assert dm_findings[0].category == Category.ACCESS_CONTROL

    def test_sandbox_disabled(self, system_info):
        """Test detection of disabled sandbox."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "settings.json"
            config = {"sandbox": {"enabled": False}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            scanner.analyze_config_file(config_file)

            sandbox_findings = [
                f for f in scanner.findings if f.id == "CLAWD-SANDBOX-001"
            ]
            assert len(sandbox_findings) == 1
            assert sandbox_findings[0].severity == Severity.CRITICAL
            assert sandbox_findings[0].category == Category.SANDBOX

    def test_docker_network_not_isolated(self, system_info):
        """Test detection of non-isolated Docker network."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config = {"sandbox": {"enabled": True, "network": "bridge"}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            scanner.analyze_config_file(config_file)

            network_findings = [
                f for f in scanner.findings if f.id == "CLAWD-SANDBOX-002"
            ]
            assert len(network_findings) == 1
            assert network_findings[0].severity == Severity.HIGH

    def test_dangerous_commands_not_blocked(self, system_info):
        """Test detection of unblocked dangerous commands."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            # Empty config with no blocked commands
            config = {}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            scanner.analyze_config_file(config_file)

            cmd_findings = [f for f in scanner.findings if f.id == "CLAWD-CMD-001"]
            assert len(cmd_findings) == 1
            assert cmd_findings[0].severity == Severity.CRITICAL
            assert cmd_findings[0].category == Category.COMMAND_INJECTION

    def test_elevated_mcp_access(self, system_info):
        """Test detection of elevated MCP tools access."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config = {"tools": {"permissions": "all"}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            scanner.analyze_config_file(config_file)

            mcp_findings = [f for f in scanner.findings if f.id == "CLAWD-MCP-001"]
            assert len(mcp_findings) == 1
            assert mcp_findings[0].severity == Severity.HIGH
            assert mcp_findings[0].category == Category.ACCESS_CONTROL

    def test_no_audit_logging(self, system_info):
        """Test detection of missing audit logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config = {"logging": {"audit": False}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            scanner.analyze_config_file(config_file)

            audit_findings = [f for f in scanner.findings if f.id == "CLAWD-AUDIT-001"]
            assert len(audit_findings) == 1
            assert audit_findings[0].severity == Severity.MEDIUM
            assert audit_findings[0].category == Category.LOGGING

    def test_weak_pairing_code(self, system_info):
        """Test detection of weak pairing codes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config = {"pairing": {"code": "1234"}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            scanner.analyze_config_file(config_file)

            pair_findings = [f for f in scanner.findings if f.id == "CLAWD-PAIR-001"]
            assert len(pair_findings) == 1
            assert pair_findings[0].severity == Severity.HIGH
            assert pair_findings[0].category == Category.AUTHENTICATION

    def test_no_rate_limiting_on_pairing(self, system_info):
        """Test detection of missing rate limiting on pairing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config = {
                "pairing": {
                    "code": "mysupersecurepairing123"
                    # No rate limiting configured
                }
            }
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            scanner.analyze_config_file(config_file)

            rate_findings = [f for f in scanner.findings if f.id == "CLAWD-PAIR-002"]
            assert len(rate_findings) == 1
            assert rate_findings[0].severity == Severity.MEDIUM

    def test_no_prompt_injection_protection(self, system_info):
        """Test detection of missing prompt injection protection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config = {"security": {"wrapUntrustedContent": False}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            scanner.analyze_config_file(config_file)

            prompt_findings = [
                f for f in scanner.findings if f.id == "CLAWD-PROMPT-001"
            ]
            assert len(prompt_findings) == 1
            assert prompt_findings[0].severity == Severity.HIGH
            assert prompt_findings[0].category == Category.PROMPT_INJECTION

    def test_secure_config_no_findings(self, system_info):
        """Test that a secure configuration produces minimal findings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config = {
                "dm": {"policy": ["user1@example.com"]},
                "sandbox": {"enabled": True, "mode": "all", "network": "none"},
                "commands": {
                    "blocked": [
                        "rm -rf",
                        "curl | bash",
                        "curl | sh",
                        "wget | bash",
                        "wget | sh",
                        "rm -r /",
                        "rm -rf /",
                        "rm -rf ~",
                        ":(){ :|:& };:",
                        "mkfs",
                        "dd if=",
                        "> /dev/sda",
                        "chmod -R 777 /",
                        "pip install --user",
                        "sudo rm",
                        "sudo chmod",
                    ]
                },
                "tools": {"permissions": "restricted"},
                "logging": {"audit": True, "session": True},
                "pairing": {
                    "code": "a-very-secure-random-pairing-code-123456",
                    "rateLimit": {"maxAttempts": 5, "windowSeconds": 300},
                },
                "security": {
                    "wrapUntrustedContent": True,
                    "contentFiltering": "strict",
                },
            }
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            scanner.analyze_config_file(config_file)

            # A fully secure config should have no findings
            assert len(scanner.findings) == 0


class TestDangerousCommands:
    """Tests for dangerous command detection."""

    def test_dangerous_commands_list(self):
        """Test that all expected dangerous commands are in the list."""
        expected_commands = [
            "rm -rf",
            "curl | bash",
            "curl | sh",
            "wget | bash",
            "wget | sh",
        ]

        for cmd in expected_commands:
            assert cmd in ClawdbotSecurityScanner.DANGEROUS_COMMANDS


class TestMoltbotNotInstalled:
    """Tests for Moltbot/Clawdbot not installed detection."""

    @pytest.fixture
    def system_info(self):
        """Create a mock system info object."""
        return SystemInfo(
            hostname="test-host",
            os_name="Linux",
            python_version="3.9.0",
        )

    def test_no_config_files_generates_info_finding(self, system_info):
        """Test that when no config files are found, an INFO finding is generated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Override home directory to a temp directory with no config files
            system_info.home_directory = tmpdir

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            findings = scanner.scan()

            # Should have exactly one finding - the "not installed" info
            install_findings = [f for f in findings if f.id == "CLAWD-INSTALL-001"]
            assert len(install_findings) == 1

            finding = install_findings[0]
            assert finding.severity == Severity.INFO
            assert finding.category == Category.CONFIG
            assert "not installed" in finding.title.lower() or "not configured" in finding.title.lower()
            assert "moltbot" in finding.description.lower() or "clawdbot" in finding.description.lower()

    def test_with_config_files_no_install_finding(self, system_info):
        """Test that analyzing a config file directly doesn't generate an install finding.

        Note: The CLAWD-INSTALL-001 finding is only generated by the scan() method
        when no config files are found. When analyze_config_file() is called directly
        with a valid config file, it should not generate an install-related finding.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock config file
            config_file = Path(tmpdir) / "config.json"
            config = {
                "dm": {"policy": ["user@example.com"]},
                "sandbox": {"enabled": True, "network": "none"},
                "commands": {"blocked": ClawdbotSecurityScanner.DANGEROUS_COMMANDS},
                "tools": {"permissions": "restricted"},
                "logging": {"audit": True, "session": True},
                "pairing": {
                    "code": "a-very-secure-random-pairing-code-123456",
                    "rateLimit": {"maxAttempts": 5, "windowSeconds": 300},
                },
                "security": {
                    "wrapUntrustedContent": True,
                    "contentFiltering": "strict",
                },
            }
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            # Analyze the config file directly - should not generate install finding
            scanner.analyze_config_file(config_file)

            # Should have no install-related findings
            install_findings = [f for f in scanner.findings if f.id == "CLAWD-INSTALL-001"]
            assert len(install_findings) == 0


class TestMoltbotConfigPaths:
    """Tests for moltbot.json and clawdbot.json config file discovery.

    These tests verify that the scanner correctly finds configuration files
    at both moltbot and clawdbot paths, matching the official moltbot repository:
    https://github.com/moltbot/moltbot
    """

    @pytest.fixture
    def system_info(self):
        """Create a mock system info object."""
        return SystemInfo(
            hostname="test-host",
            os_name="Linux",
            python_version="3.9.0",
        )

    def test_finds_moltbot_json_in_moltbot_dir(self, system_info):
        """Test that moltbot.json is found in ~/.moltbot/ directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system_info.home_directory = tmpdir

            # Create ~/.moltbot/moltbot.json (canonical new path)
            moltbot_dir = Path(tmpdir) / ".moltbot"
            moltbot_dir.mkdir()
            config_file = moltbot_dir / "moltbot.json"
            config = {"dm": {"policy": "all"}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            found_files = scanner._find_config_files()

            assert len(found_files) >= 1
            assert any("moltbot.json" in str(f) for f in found_files)

    def test_finds_clawdbot_json_in_moltbot_dir(self, system_info):
        """Test that clawdbot.json is found in ~/.moltbot/ directory (legacy filename)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system_info.home_directory = tmpdir

            # Create ~/.moltbot/clawdbot.json (legacy filename in new dir)
            moltbot_dir = Path(tmpdir) / ".moltbot"
            moltbot_dir.mkdir()
            config_file = moltbot_dir / "clawdbot.json"
            config = {"dm": {"policy": "all"}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            found_files = scanner._find_config_files()

            assert len(found_files) >= 1
            assert any("clawdbot.json" in str(f) for f in found_files)

    def test_finds_moltbot_json_in_clawdbot_dir(self, system_info):
        """Test that moltbot.json is found in ~/.clawdbot/ directory (new filename in legacy dir)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system_info.home_directory = tmpdir

            # Create ~/.clawdbot/moltbot.json (new filename in legacy dir)
            clawdbot_dir = Path(tmpdir) / ".clawdbot"
            clawdbot_dir.mkdir()
            config_file = clawdbot_dir / "moltbot.json"
            config = {"dm": {"policy": "all"}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            found_files = scanner._find_config_files()

            assert len(found_files) >= 1
            assert any("moltbot.json" in str(f) for f in found_files)

    def test_finds_clawdbot_json_in_clawdbot_dir(self, system_info):
        """Test that clawdbot.json is found in ~/.clawdbot/ directory (full legacy path)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system_info.home_directory = tmpdir

            # Create ~/.clawdbot/clawdbot.json (full legacy path)
            clawdbot_dir = Path(tmpdir) / ".clawdbot"
            clawdbot_dir.mkdir()
            config_file = clawdbot_dir / "clawdbot.json"
            config = {"dm": {"policy": "all"}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            found_files = scanner._find_config_files()

            assert len(found_files) >= 1
            assert any("clawdbot.json" in str(f) for f in found_files)

    def test_finds_both_moltbot_and_clawdbot_configs(self, system_info):
        """Test that scanner finds configs in both ~/.moltbot/ and ~/.clawdbot/ directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system_info.home_directory = tmpdir

            # Create both directories with config files
            moltbot_dir = Path(tmpdir) / ".moltbot"
            moltbot_dir.mkdir()
            (moltbot_dir / "moltbot.json").write_text('{"dm": {"policy": "all"}}')

            clawdbot_dir = Path(tmpdir) / ".clawdbot"
            clawdbot_dir.mkdir()
            (clawdbot_dir / "clawdbot.json").write_text('{"dm": {"policy": "all"}}')

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            found_files = scanner._find_config_files()

            # Should find both config files
            assert len(found_files) >= 2
            file_names = [f.name for f in found_files]
            assert "moltbot.json" in file_names
            assert "clawdbot.json" in file_names

    def test_scans_moltbot_json_for_security_issues(self, system_info):
        """Test that moltbot.json files are properly scanned for security issues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system_info.home_directory = tmpdir

            # Create ~/.moltbot/moltbot.json with insecure config
            moltbot_dir = Path(tmpdir) / ".moltbot"
            moltbot_dir.mkdir()
            config_file = moltbot_dir / "moltbot.json"
            config = {
                "dm": {"policy": "all"},  # Insecure: allows all users
                "sandbox": {"enabled": False},  # Insecure: sandbox disabled
            }
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            findings = scanner.scan()

            # Should detect the security issues
            assert len(findings) >= 2
            finding_ids = [f.id for f in findings]
            assert "CLAWD-DM-001" in finding_ids  # DM policy issue
            assert "CLAWD-SANDBOX-001" in finding_ids  # Sandbox disabled

    def test_scans_clawdbot_json_for_security_issues(self, system_info):
        """Test that clawdbot.json files are properly scanned for security issues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system_info.home_directory = tmpdir

            # Create ~/.clawdbot/clawdbot.json with insecure config
            clawdbot_dir = Path(tmpdir) / ".clawdbot"
            clawdbot_dir.mkdir()
            config_file = clawdbot_dir / "clawdbot.json"
            config = {
                "dm": {"policy": "all"},  # Insecure: allows all users
                "pairing": {"code": "1234"},  # Insecure: weak pairing code
            }
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            findings = scanner.scan()

            # Should detect the security issues
            assert len(findings) >= 2
            finding_ids = [f.id for f in findings]
            assert "CLAWD-DM-001" in finding_ids  # DM policy issue
            assert "CLAWD-PAIR-001" in finding_ids  # Weak pairing code


class TestClaudeDesktopNotScanned:
    """Tests to verify Claude Desktop paths are NOT scanned for Moltbot/Clawdbot issues.

    Claude Desktop (.claude/, Claude/) is a separate application from Moltbot/Clawdbot.
    The security scanner should only scan Moltbot/Clawdbot configuration files,
    not Claude Desktop files.
    """

    @pytest.fixture
    def system_info(self):
        """Create a mock system info object."""
        return SystemInfo(
            hostname="test-host",
            os_name="Linux",
            python_version="3.9.0",
        )

    def test_claude_desktop_config_not_scanned(self, system_info):
        """Test that claude_desktop_config.json is NOT scanned for Moltbot issues.

        When only Claude Desktop is installed (not Moltbot/Clawdbot), the scanner
        should generate a 'not installed' finding rather than scanning the Claude
        Desktop config file.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            system_info.home_directory = tmpdir

            # Create a Claude Desktop config file (NOT a Moltbot config)
            claude_dir = Path(tmpdir) / ".config" / "claude"
            claude_dir.mkdir(parents=True)
            config_file = claude_dir / "claude_desktop_config.json"
            # This config would trigger findings if it were scanned as Moltbot config
            config = {"dm": {"policy": "all"}, "sandbox": {"enabled": False}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            findings = scanner.scan()

            # Should NOT find the DM policy or sandbox issues from Claude Desktop config
            finding_ids = [f.id for f in findings]
            assert "CLAWD-DM-001" not in finding_ids
            assert "CLAWD-SANDBOX-001" not in finding_ids

            # Should instead get the "not installed" finding since no Moltbot config exists
            assert "CLAWD-INSTALL-001" in finding_ids

    def test_dot_claude_directory_not_scanned(self, system_info):
        """Test that the .claude directory is NOT scanned for Moltbot issues.

        The ~/.claude/ directory is for Claude Desktop, not Moltbot/Clawdbot.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            system_info.home_directory = tmpdir

            # Create a .claude directory with a config file
            claude_dir = Path(tmpdir) / ".claude"
            claude_dir.mkdir()
            config_file = claude_dir / "settings.json"
            # This config would trigger findings if it were scanned as Moltbot config
            config = {"dm": {"policy": "all"}}
            config_file.write_text(json.dumps(config))

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            findings = scanner.scan()

            # Should NOT find DM policy issue from .claude directory
            dm_findings = [f for f in findings if f.id == "CLAWD-DM-001"]
            assert len(dm_findings) == 0

            # Should get the "not installed" finding since no Moltbot config exists
            install_findings = [f for f in findings if f.id == "CLAWD-INSTALL-001"]
            assert len(install_findings) == 1

    def test_only_moltbot_clawdbot_paths_scanned(self, system_info):
        """Test that only Moltbot/Clawdbot paths are scanned, not Claude Desktop."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system_info.home_directory = tmpdir

            # Create BOTH Claude Desktop and Moltbot configs
            # Claude Desktop config (should NOT be scanned)
            claude_dir = Path(tmpdir) / ".claude"
            claude_dir.mkdir()
            claude_config = claude_dir / "settings.json"
            claude_config.write_text('{"dm": {"policy": "all"}}')

            # Moltbot config (SHOULD be scanned)
            moltbot_dir = Path(tmpdir) / ".moltbot"
            moltbot_dir.mkdir()
            moltbot_config = moltbot_dir / "moltbot.json"
            moltbot_config.write_text('{"sandbox": {"enabled": false}}')

            scanner = ClawdbotSecurityScanner(system_info, verbose=False)
            findings = scanner.scan()

            finding_ids = [f.id for f in findings]

            # Should find sandbox issue from Moltbot config
            assert "CLAWD-SANDBOX-001" in finding_ids

            # The DM finding would ONLY come from the .claude config if it was scanned
            # Since we also have dangerous commands not blocked, there should be that finding
            # But we can verify that no "CLAWD-INSTALL-001" is present since Moltbot config exists
            assert "CLAWD-INSTALL-001" not in finding_ids
