"""
Network Analyzer Module

This module analyzes network exposure and firewall configuration.
"""

import subprocess
from typing import List

from clawd_for_dummies.models.finding import Finding, Severity, Category
from clawd_for_dummies.models.system_info import SystemInfo
from clawd_for_dummies.engine.base_scanner import BaseScanner


class NetworkAnalyzer(BaseScanner):
    """
    Scanner for analyzing network exposure.

    This scanner checks for:
    - Public IP exposure
    - Firewall rules
    - UPnP/NAT-PMP port forwarding
    - Network interface configuration
    """

    CLAWDBOT_PORT = 18789

    def __init__(self, system_info: SystemInfo, verbose: bool = False):
        """Initialize the network analyzer."""
        super().__init__(system_info, verbose)
        self.findings: List[Finding] = []

    @classmethod
    def get_name(cls) -> str:
        """Get scanner name."""
        return "Network Analyzer"

    @classmethod
    def get_description(cls) -> str:
        """Get scanner description."""
        return "Analyzes network exposure and firewall configuration"

    def scan(self) -> List[Finding]:
        """
        Perform network security scan.

        Returns:
            List of security findings
        """
        self.findings = []

        self.log("Analyzing network configuration...")

        # Check for public IP
        self._check_public_ip()

        # Check firewall status
        self._check_firewall()

        # Check for port forwarding
        self._check_port_forwarding()

        return self.findings

    def _check_public_ip(self) -> None:
        """Check if system has a public IP address."""
        # Check if any local IP is not in private ranges
        private_ranges = [
            ("10.0.0.0", "10.255.255.255"),
            ("172.16.0.0", "172.31.255.255"),
            ("192.168.0.0", "192.168.255.255"),
            ("127.0.0.0", "127.255.255.255"),
        ]

        has_public_ip = False

        for ip in self.system_info.local_ips:
            is_private = False
            for start, end in private_ranges:
                if self._ip_in_range(ip, start, end):
                    is_private = True
                    break

            if not is_private:
                has_public_ip = True
                break

        if has_public_ip:
            finding = Finding(
                id="CLAWD-NET-001",
                title="System Has Public IP Address",
                description=(
                    "Your system has a public IP address directly assigned to it. "
                    "This means it's accessible from the internet without NAT or firewall protection. "
                    "If Clawdbot is exposed, attackers can reach it directly."
                ),
                severity=Severity.HIGH,
                category=Category.NETWORK,
                cvss_score=7.0,
                evidence={
                    "public_ips": [
                        ip
                        for ip in self.system_info.local_ips
                        if not any(
                            self._ip_in_range(ip, s, e) for s, e in private_ranges
                        )
                    ],
                },
                location="Network interface",
                remediation=(
                    "Place your system behind a firewall or NAT router. "
                    "Do not expose services directly to the internet without proper security."
                ),
                remediation_steps=[
                    "Configure a firewall to block incoming connections",
                    "Place system behind a NAT router",
                    "Use a VPN for remote access instead of exposing ports",
                    "Regularly monitor for unauthorized access attempts",
                ],
                reference_links=[
                    "https://www.cisa.gov/news-events/news/cisa-releases-firewall-guidance",
                ],
                fix_prompt=(
                    "Place this system behind a NAT router or firewall to prevent direct "
                    "internet exposure. Configure the firewall to block all incoming connections "
                    "to port 18789 from external networks. If remote access is needed, use a VPN "
                    "or SSH tunnel instead of exposing the Clawdbot port directly to the internet."
                ),
            )
            self.findings.append(finding)

    def _check_firewall(self) -> None:
        """Check if firewall is enabled."""
        firewall_enabled = False

        try:
            if self.system_info.is_windows:
                # Check Windows Firewall
                result = subprocess.run(
                    ["netsh", "advfirewall", "show", "currentprofile"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                firewall_enabled = "ON" in result.stdout or "State ON" in result.stdout

            elif self.system_info.is_macos:
                # Check macOS firewall
                result = subprocess.run(
                    [
                        "sudo",
                        "/usr/libexec/ApplicationFirewall/socketfilterfw",
                        "--getglobalstate",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                firewall_enabled = "enabled" in result.stdout.lower()

            else:  # Linux
                # Check various firewall tools
                for cmd in ["ufw", "firewalld", "iptables"]:
                    try:
                        if cmd == "ufw":
                            result = subprocess.run(
                                ["sudo", "ufw", "status"],
                                capture_output=True,
                                text=True,
                                timeout=5,
                            )
                            firewall_enabled = "active" in result.stdout.lower()
                        elif cmd == "firewalld":
                            result = subprocess.run(
                                ["sudo", "firewall-cmd", "--state"],
                                capture_output=True,
                                text=True,
                                timeout=5,
                            )
                            firewall_enabled = result.returncode == 0
                        elif cmd == "iptables":
                            result = subprocess.run(
                                ["sudo", "iptables", "-L", "-n"],
                                capture_output=True,
                                text=True,
                                timeout=5,
                            )
                            # Check if there are any rules
                            firewall_enabled = (
                                len(result.stdout.strip().split("\n")) > 2
                            )

                        if firewall_enabled:
                            break

                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        continue

        except Exception as e:
            self.log(f"Error checking firewall: {e}")

        if not firewall_enabled:
            finding = Finding(
                id="CLAWD-NET-002",
                title="Firewall Not Detected or Disabled",
                description=(
                    "No active firewall was detected on your system. "
                    "A firewall helps protect your system by blocking unauthorized incoming connections. "
                    "Without a firewall, exposed services are more vulnerable to attack."
                ),
                severity=Severity.MEDIUM,
                category=Category.NETWORK,
                cvss_score=5.0,
                evidence={
                    "firewall_status": "not detected",
                },
                location="System firewall",
                remediation=("Enable and configure a firewall on your system."),
                remediation_steps=[
                    "Windows: Open Windows Security > Firewall & network protection > Enable",
                    "macOS: System Preferences > Security & Privacy > Firewall > Turn On",
                    "Linux: Install and configure ufw, firewalld, or iptables",
                    "Block incoming connections to port 18789 unless specifically needed",
                ],
                reference_links=[
                    "https://www.cisa.gov/news-events/news/cisa-releases-firewall-guidance",
                ],
                fix_prompt=(
                    "Enable the system firewall to protect against unauthorized network access. "
                    "On Linux: 'sudo ufw enable && sudo ufw deny 18789'. "
                    "On macOS: System Preferences > Security & Privacy > Firewall > Turn On. "
                    "On Windows: Windows Security > Firewall & network protection > Turn on."
                ),
            )
            self.findings.append(finding)

    def _check_port_forwarding(self) -> None:
        """Check for UPnP/NAT-PMP port forwarding."""
        # This is a simplified check - full UPnP detection would require additional libraries

        # Check if we can detect any port forwarding
        # This is mostly informational as true detection requires external services

        self.log("Note: Full port forwarding detection requires external check")

        # Add informational finding about UPnP risks
        finding = Finding(
            id="CLAWD-NET-003",
            title="UPnP/NAT-PMP Port Forwarding Risk",
            description=(
                "If your router has UPnP or NAT-PMP enabled, applications can automatically "
                "open ports on your firewall without your knowledge. This could expose your "
                "Clawdbot instance to the internet even if you didn't manually configure port forwarding."
            ),
            severity=Severity.INFO,
            category=Category.NETWORK,
            cvss_score=0.0,
            evidence={
                "note": "Manual verification required",
            },
            location="Router configuration",
            remediation=(
                "Disable UPnP/NAT-PMP on your router for better security control."
            ),
            remediation_steps=[
                "Log into your router's admin interface",
                "Find UPnP or NAT-PMP settings (usually under Advanced > NAT)",
                "Disable UPnP and NAT-PMP",
                "Manually configure any needed port forwards",
            ],
            reference_links=[
                "https://www.us-cert.gov/ncas/alerts/TA14-017A",
            ],
            fix_prompt=(
                "Log into your router's admin interface (usually 192.168.1.1 or 192.168.0.1) "
                "and disable UPnP and NAT-PMP features. Look under Advanced > NAT or similar "
                "settings. This prevents applications from automatically opening ports to the "
                "internet without your knowledge. Manually configure only the port forwards you need."
            ),
        )
        self.findings.append(finding)

    def _ip_in_range(self, ip: str, start: str, end: str) -> bool:
        """Check if an IP address is within a range."""
        try:
            ip_int = self._ip_to_int(ip)
            start_int = self._ip_to_int(start)
            end_int = self._ip_to_int(end)
            return start_int <= ip_int <= end_int
        except Exception:
            return False

    def _ip_to_int(self, ip: str) -> int:
        """Convert IP address to integer."""
        parts = ip.split(".")
        return (
            (int(parts[0]) << 24)
            + (int(parts[1]) << 16)
            + (int(parts[2]) << 8)
            + int(parts[3])
        )
