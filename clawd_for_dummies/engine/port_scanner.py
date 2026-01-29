"""
Port scanner for detecting exposed Clawdbot gateway and authentication issues.
"""

import socket
import subprocess
from typing import List

from clawd_for_dummies.models.finding import Finding, Severity, Category
from clawd_for_dummies.models.system_info import SystemInfo
from clawd_for_dummies.engine.base_scanner import BaseScanner


class PortScanner(BaseScanner):
    """Scans for exposed ports and authentication bypass vulnerabilities."""

    CLAWDBOT_PORT = 18789

    def __init__(self, system_info: SystemInfo, verbose: bool = False):
        super().__init__(system_info, verbose)
        self.findings: List[Finding] = []

    @classmethod
    def get_name(cls) -> str:
        return "Port Scanner"

    @classmethod
    def get_description(cls) -> str:
        return "Checks for exposed ports and authentication bypass vulnerabilities"

    def scan(self) -> List[Finding]:
        self.findings = []
        self.log("Checking Clawdbot gateway port...")

        port_status = self._check_port_status(self.CLAWDBOT_PORT)

        if port_status["is_listening"]:
            self.log(f"Port {self.CLAWDBOT_PORT} is listening")

            if port_status["bind_address"] == "0.0.0.0":
                self._add_exposed_port_finding(port_status)
            elif port_status["bind_address"] == "127.0.0.1":
                self.log("Port is bound to localhost only (good)")
                self._check_auth_bypass()
            else:
                self.log(f"Port bound to {port_status['bind_address']}")
                self._check_auth_bypass()
        else:
            self.log(
                f"Port {self.CLAWDBOT_PORT} is not listening (Clawdbot may not be running)"
            )

        return self.findings

    def _check_port_status(self, port: int) -> dict:
        result = {
            "is_listening": False,
            "bind_address": None,
            "process_name": None,
            "pid": None,
        }

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)

            localhost_result = sock.connect_ex(("127.0.0.1", port))
            sock.close()

            if localhost_result == 0:
                result["is_listening"] = True

                if self.system_info.is_windows:
                    result.update(self._get_windows_port_info(port))
                else:
                    result.update(self._get_unix_port_info(port))

        except Exception as e:
            self.log(f"Error checking port: {e}")

        return result

    def _get_windows_port_info(self, port: int) -> dict:
        result = {"bind_address": "unknown", "process_name": None, "pid": None}

        try:
            output = subprocess.check_output(
                ["netstat", "-ano"],
                text=True,
                stderr=subprocess.DEVNULL,
            )

            for line in output.split("\n"):
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        local_addr = parts[1]
                        if ":" in local_addr:
                            bind_addr = local_addr.rsplit(":", 1)[0]
                            result["bind_address"] = bind_addr
                            result["pid"] = parts[-1]
                            break

        except Exception as e:
            self.log(f"Error getting Windows port info: {e}")

        return result

    def _get_unix_port_info(self, port: int) -> dict:
        result = {"bind_address": "unknown", "process_name": None, "pid": None}

        try:
            try:
                output = subprocess.check_output(
                    ["lsof", "-i", f"tcp:{port}", "-P", "-n"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )

                for line in output.split("\n")[1:]:
                    parts = line.split()
                    if len(parts) >= 9:
                        name_field = parts[8]
                        if "*" in name_field or ":" in name_field:
                            if name_field.startswith("*:"):
                                result["bind_address"] = "0.0.0.0"
                            elif name_field.startswith("127."):
                                result["bind_address"] = "127.0.0.1"
                            result["process_name"] = parts[0]
                            result["pid"] = parts[1]
                            break

            except (subprocess.CalledProcessError, FileNotFoundError):
                output = subprocess.check_output(
                    ["netstat", "-tlnp"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )

                for line in output.split("\n"):
                    if f":{port}" in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            local_addr = parts[3]
                            if local_addr.startswith(
                                "0.0.0.0"
                            ) or local_addr.startswith("*"):
                                result["bind_address"] = "0.0.0.0"
                            elif local_addr.startswith("127."):
                                result["bind_address"] = "127.0.0.1"

                            if len(parts) >= 7:
                                process_info = parts[-1]
                                if "/" in process_info:
                                    result["pid"] = process_info.split("/")[0]
                                    result["process_name"] = process_info.split("/")[1]
                            break

        except Exception as e:
            self.log(f"Error getting Unix port info: {e}")

        return result

    def _check_auth_bypass(self) -> None:
        self.log("Checking for authentication bypass...")

        try:
            import urllib.request

            req = urllib.request.Request(
                f"http://127.0.0.1:{self.CLAWDBOT_PORT}/",
                method="GET",
            )

            try:
                response = urllib.request.urlopen(req, timeout=5)

                if response.status == 200:
                    self._add_auth_bypass_finding()

            except urllib.error.HTTPError as e:
                if e.code == 401:
                    self.log("Authentication required (good)")
                else:
                    self.log(f"HTTP error: {e.code}")

        except Exception as e:
            self.log(f"Could not test auth bypass: {e}")

    def _add_exposed_port_finding(self, port_status: dict) -> None:
        finding = Finding(
            id="CLAWD-PORT-001",
            title="Clawdbot Gateway Exposed to Network",
            description=(
                "Your Clawdbot gateway (port 18789) is bound to 0.0.0.0, "
                "meaning it's accessible from ANY computer on your network "
                "or the internet. This allows anyone to connect to your "
                "Clawdbot instance without authentication."
            ),
            severity=Severity.CRITICAL,
            category=Category.PORT,
            cvss_score=9.8,
            evidence={
                "port": self.CLAWDBOT_PORT,
                "bind_address": port_status.get("bind_address"),
                "process": port_status.get("process_name"),
                "pid": port_status.get("pid"),
            },
            location=f"Port {self.CLAWDBOT_PORT} bound to 0.0.0.0",
            remediation=(
                "Configure Clawdbot to bind only to localhost (127.0.0.1) "
                "or enable authentication."
            ),
            remediation_steps=[
                "Open your Clawdbot configuration file",
                "Find the 'gateway' or 'server' section",
                "Change 'bind' from '0.0.0.0' to '127.0.0.1'",
                "Alternatively, enable authentication with 'requireAuthentication: true'",
                "Restart Moltbot/Clawdbot to apply changes",
            ],
            reference_links=[
                "https://github.com/jasondsmith72/Clawdbot",
                "https://docs.clawdbot.dev/security",
            ],
            fix_prompt=(
                "Bind the Clawdbot gateway to 127.0.0.1 instead of 0.0.0.0 to prevent "
                "network exposure. Update the gateway.host or bind setting in moltbot.json "
                "to '127.0.0.1' and restart the service. If remote access is required, "
                "enable authentication with 'requireAuthentication: true' and set a strong authToken."
            ),
        )

        self.findings.append(finding)

    def _add_auth_bypass_finding(self) -> None:
        finding = Finding(
            id="CLAWD-AUTH-001",
            title="Authentication Bypass Vulnerability",
            description=(
                "Your Clawdbot gateway accepted a connection without "
                "requiring authentication. This is likely due to the "
                "reverse proxy authentication bypass vulnerability where "
                "all external traffic appears as localhost (127.0.0.1), "
                "triggering auto-approval. Attackers can exploit this to "
                "gain full access to your Clawdbot instance."
            ),
            severity=Severity.CRITICAL,
            category=Category.AUTHENTICATION,
            cvss_score=10.0,
            evidence={
                "port": self.CLAWDBOT_PORT,
                "test_method": "HTTP request without credentials",
            },
            location=f"Port {self.CLAWDBOT_PORT}",
            remediation=(
                "Enable authentication in Clawdbot configuration immediately. "
                "Do not rely on localhost auto-approval when behind a reverse proxy."
            ),
            remediation_steps=[
                "Open your Clawdbot/Moltbot configuration file (moltbot.json or clawdbot.json)",
                "Add or set 'requireAuthentication' to true",
                "Set a strong password in 'authToken' or 'password' field",
                "If using a reverse proxy, ensure auth is enabled",
                "Restart Moltbot/Clawdbot to apply changes",
                "Test that authentication is required by trying to connect",
            ],
            reference_links=[
                "https://github.com/jasondsmith72/Clawdbot",
                "https://www.reddit.com/r/ChatGPT/comments/1qodjzm/",
            ],
            fix_prompt=(
                "Enable authentication in the Clawdbot/Moltbot configuration to fix "
                "this critical vulnerability. Open moltbot.json or clawdbot.json, set "
                "'requireAuthentication' to true, and add a strong 'authToken' value "
                "(use a random 32+ character string). If behind a reverse proxy, never "
                "rely on localhost auto-approval. Restart the service after changes."
            ),
        )

        self.findings.append(finding)
