"""
Secure connector for Clawdbot/Moltbot gateway handshake and communication.

Supports both Clawdbot (legacy) and Moltbot (https://github.com/moltbot/moltbot).
Default port: 18789
"""

import hashlib
import hmac
import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from clawd_for_dummies.utils.secure import (
    SecureDict,
    generate_secure_token,
    sanitize_string,
)


class ConnectionStatus(Enum):
    """Connection status states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    AWAITING_PERMISSION = "awaiting_permission"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    ERROR = "error"

    def __str__(self) -> str:
        return self.value


class PermissionLevel(Enum):
    """Permission levels for gateway access."""

    NONE = "none"
    READ_ONLY = "read_only"
    SCAN = "scan"
    FULL = "full"

    def __str__(self) -> str:
        return self.value


@dataclass
class HandshakeResult:
    """Result of a handshake attempt."""

    success: bool
    status: ConnectionStatus
    permission_level: PermissionLevel = PermissionLevel.NONE
    session_id: str = ""
    clawdbot_version: str = ""
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None
    user_guidance: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "status": self.status.value,
            "permission_level": self.permission_level.value,
            "session_id": self.session_id,
            "clawdbot_version": self.clawdbot_version,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
            "user_guidance": self.user_guidance,
        }

    def get_user_friendly_message(self) -> str:
        """Generate a user-friendly message for display in UI/CLI."""
        if self.success:
            return self.message or "Successfully connected to Moltbot!"

        # User-friendly error messages
        lines = []

        # Match both legacy "Clawdbot" and new "Moltbot" error messages for backward compatibility
        if self.error and "not detected" in self.error.lower():
            lines.append("╔═══════════════════════════════════════════════════════════════╗")
            lines.append("║           Moltbot/Clawdbot Not Detected                       ║")
            lines.append("╚═══════════════════════════════════════════════════════════════╝")
            lines.append("")
            lines.append("  We couldn't find a running Moltbot or Clawdbot instance.")
            lines.append("")
            lines.append("  📋 WHAT THIS MEANS:")
            lines.append("     Moltbot (or Clawdbot) is not currently running on your")
            lines.append("     computer, or it may not be installed yet.")
            lines.append("")
            lines.append("  🔧 HOW TO FIX:")
            lines.append("")
            lines.append("     If Moltbot is already installed:")
            lines.append("       1. Start Moltbot with: moltbot gateway --port 18789")
            lines.append("       2. Wait for the gateway to start")
            lines.append("       3. Run this scanner again")
            lines.append("")
            lines.append("     If Moltbot is NOT installed:")
            lines.append("       1. Install Node.js (version 22 or higher)")
            lines.append("       2. Run: npm install -g moltbot@latest")
            lines.append("       3. Run: moltbot onboard --install-daemon")
            lines.append("       4. Start the gateway: moltbot gateway --port 18789")
            lines.append("       5. Run this scanner again")
            lines.append("")
            lines.append("  📚 DOCUMENTATION:")
            lines.append("     • Getting Started: https://docs.molt.bot/start/getting-started")
            lines.append("     • Installation: https://docs.molt.bot/install")
            lines.append("     • GitHub: https://github.com/moltbot/moltbot")
            lines.append("")
            lines.append("  💡 TIP: You can still run the local security scan without")
            lines.append("     Moltbot connected. The scanner will check for potential")
            lines.append("     vulnerabilities in configuration files on your system.")
            lines.append("")
        elif self.error == "Permission denied":
            lines.append("╔═══════════════════════════════════════════════════════════════╗")
            lines.append("║              Permission Denied                                ║")
            lines.append("╚═══════════════════════════════════════════════════════════════╝")
            lines.append("")
            lines.append("  The security scan was denied by the user.")
            lines.append("")
            lines.append("  🔧 HOW TO FIX:")
            lines.append("     1. Run the scanner again")
            lines.append("     2. Accept the permission request when prompted")
            lines.append("")
        else:
            lines.append(f"  ⚠️  Error: {self.error or 'Unknown error'}")
            if self.message:
                lines.append(f"  Message: {self.message}")

        if self.user_guidance:
            lines.append("")
            lines.append(f"  Additional guidance: {self.user_guidance}")

        return "\n".join(lines)


@dataclass
class SecurityCheckRequest:
    """Request for a security check."""

    check_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    session_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityCheckResponse:
    """Response from a security check."""

    check_type: str
    success: bool
    result: Dict[str, Any] = field(default_factory=dict)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class ClawdbotConnector:
    """Connector for Clawdbot/Moltbot gateway communication."""

    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 18789
    HANDSHAKE_TIMEOUT = 10
    REQUEST_TIMEOUT = 30

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        verbose: bool = False,
    ) -> None:
        self._host = sanitize_string(host)
        self._port = port
        self._verbose = verbose
        self._status = ConnectionStatus.DISCONNECTED
        self._permission_level = PermissionLevel.NONE
        self._secure_data = SecureDict()
        self._session_id: str = ""
        self._connected_at: Optional[datetime] = None
        self._permission_callback: Optional[Callable[[str], bool]] = None

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def status(self) -> ConnectionStatus:
        return self._status

    @property
    def permission_level(self) -> PermissionLevel:
        return self._permission_level

    @property
    def is_connected(self) -> bool:
        return self._status in (
            ConnectionStatus.CONNECTED,
            ConnectionStatus.AUTHENTICATED,
        )

    @property
    def session_id(self) -> str:
        return self._session_id

    def set_permission_callback(self, callback: Callable[[str], bool]) -> None:
        self._permission_callback = callback

    def discover(self) -> bool:
        self._log("Discovering Clawdbot instance...")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)

            result = sock.connect_ex((self._host, self._port))
            sock.close()

            if result == 0:
                self._log(f"Clawdbot detected at {self._host}:{self._port}")
                return True
            else:
                self._log("Clawdbot not detected on default port")
                return False

        except socket.error as e:
            self._log(f"Socket error during discovery: {e}")
            return False

    def handshake(
        self,
        requested_permission: PermissionLevel = PermissionLevel.SCAN,
        auth_token: Optional[str] = None,
    ) -> HandshakeResult:
        """
        Perform a secure handshake with Clawdbot/Moltbot gateway. This method
        establishes a connection, generates session credentials, requests
        permission, and returns the handshake result.
        """
        self._log("Initiating handshake with Clawdbot...")
        self._status = ConnectionStatus.CONNECTING

        self._session_id = generate_secure_token(16)
        nonce = generate_secure_token(16)

        if auth_token:
            self._secure_data.set("auth_token", auth_token, sensitive=True)

        try:
            if not self.discover():
                return HandshakeResult(
                    success=False,
                    status=ConnectionStatus.ERROR,
                    error="Moltbot not detected",
                    message="Could not find a running Moltbot/Clawdbot instance",
                    user_guidance=(
                        "Make sure Moltbot is installed and the gateway is running. "
                        "Run 'moltbot gateway --port 18789' to start it."
                    ),
                )

            self._status = ConnectionStatus.AWAITING_PERMISSION

            permission_message = (
                f"ClawdForDummies Security Scanner requests "
                f"'{requested_permission.value}' access to scan your "
                f"Moltbot configuration for security vulnerabilities.\n\n"
                f"Session ID: {self._session_id[:8]}...\n"
                f"This is a local scan only - no data leaves your computer."
            )

            if self._permission_callback:
                granted = self._permission_callback(permission_message)
                if not granted:
                    self._status = ConnectionStatus.DISCONNECTED
                    return HandshakeResult(
                        success=False,
                        status=ConnectionStatus.DISCONNECTED,
                        error="Permission denied",
                        message="User denied permission for security scan",
                    )
            else:
                self._log(f"Permission request: {permission_message}")

            handshake_payload = {
                "action": "security_scan_handshake",
                "session_id": self._session_id,
                "nonce": nonce,
                "timestamp": datetime.now().isoformat(),
                "requested_permission": requested_permission.value,
                "scanner_version": "1.0.0",
            }

            signature = self._create_signature(
                json.dumps(handshake_payload, sort_keys=True)
            )
            handshake_payload["signature"] = signature

            response = self._send_request(
                "/api/security/handshake",
                handshake_payload,
                timeout=self.HANDSHAKE_TIMEOUT,
            )

            if response and response.get("success"):
                self._status = ConnectionStatus.AUTHENTICATED
                self._permission_level = PermissionLevel(
                    response.get("granted_permission", "scan")
                )
                self._connected_at = datetime.now()

                return HandshakeResult(
                    success=True,
                    status=ConnectionStatus.AUTHENTICATED,
                    permission_level=self._permission_level,
                    session_id=self._session_id,
                    clawdbot_version=response.get("version", "unknown"),
                    message="Successfully connected to Clawdbot",
                )
            else:
                self._status = ConnectionStatus.CONNECTED
                self._permission_level = PermissionLevel.READ_ONLY

                return HandshakeResult(
                    success=True,
                    status=ConnectionStatus.CONNECTED,
                    permission_level=PermissionLevel.READ_ONLY,
                    session_id=self._session_id,
                    message=(
                        "Connected to Clawdbot (basic mode - "
                        "API handshake not supported)"
                    ),
                )

        except urllib.error.HTTPError as e:
            self._status = ConnectionStatus.ERROR
            error_msg = f"HTTP error: {e.code}"
            self._log(error_msg)
            return HandshakeResult(
                success=False,
                status=ConnectionStatus.ERROR,
                error=error_msg,
            )

        except urllib.error.URLError:
            self._status = ConnectionStatus.CONNECTED
            self._permission_level = PermissionLevel.READ_ONLY
            return HandshakeResult(
                success=True,
                status=ConnectionStatus.CONNECTED,
                permission_level=PermissionLevel.READ_ONLY,
                session_id=self._session_id,
                message="Connected to Clawdbot (basic mode)",
            )

        except Exception as e:
            self._status = ConnectionStatus.ERROR
            self._log(f"Handshake error: {e}")
            return HandshakeResult(
                success=False,
                status=ConnectionStatus.ERROR,
                error=str(e),
            )

    def request_security_check(
        self,
        check_type: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> SecurityCheckResponse:
        if not self.is_connected:
            return SecurityCheckResponse(
                check_type=check_type,
                success=False,
                error="Not connected to Clawdbot",
            )

        if self._permission_level == PermissionLevel.NONE:
            return SecurityCheckResponse(
                check_type=check_type,
                success=False,
                error="No permission granted for security checks",
            )

        request = SecurityCheckRequest(
            check_type=check_type,
            parameters=parameters or {},
            session_id=self._session_id,
        )

        try:
            response = self._send_request(
                "/api/security/check",
                {
                    "check_type": request.check_type,
                    "parameters": request.parameters,
                    "session_id": request.session_id,
                    "timestamp": request.timestamp.isoformat(),
                },
                timeout=self.REQUEST_TIMEOUT,
            )

            if response:
                return SecurityCheckResponse(
                    check_type=check_type,
                    success=True,
                    result=response.get("result", {}),
                    findings=response.get("findings", []),
                )
            else:
                return SecurityCheckResponse(
                    check_type=check_type,
                    success=False,
                    error="Empty response from Clawdbot",
                )

        except Exception as e:
            return SecurityCheckResponse(
                check_type=check_type,
                success=False,
                error=str(e),
            )

    def get_configuration(self) -> Optional[Dict[str, Any]]:
        if not self.is_connected:
            return None

        try:
            response = self._send_request(
                "/api/config",
                {"session_id": self._session_id},
                timeout=self.REQUEST_TIMEOUT,
            )
            return response
        except Exception as e:
            self._log(f"Error getting configuration: {e}")
            return None

    def verify_security_settings(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {
            "verified": False,
            "checks": {},
            "timestamp": datetime.now().isoformat(),
        }

        if not self.is_connected:
            results["error"] = "Not connected"
            return results

        security_checks = [
            ("authentication", "Verify authentication is enabled"),
            ("sandbox", "Verify sandbox is enabled"),
            ("network_binding", "Verify network binding is secure"),
            ("audit_logging", "Verify audit logging is enabled"),
            ("command_blocking", "Verify dangerous commands are blocked"),
        ]

        for check_id, description in security_checks:
            try:
                response = self.request_security_check(check_id)
                results["checks"][check_id] = {
                    "description": description,
                    "passed": response.success and not response.findings,
                    "findings": response.findings,
                    "error": response.error,
                }
            except Exception as e:
                results["checks"][check_id] = {
                    "description": description,
                    "passed": False,
                    "error": str(e),
                }

        all_passed = all(
            check.get("passed", False) for check in results["checks"].values()
        )
        results["verified"] = all_passed

        return results

    def disconnect(self) -> None:
        self._log("Disconnecting from Clawdbot...")

        try:
            if self.is_connected and self._session_id:
                try:
                    self._send_request(
                        "/api/security/disconnect",
                        {"session_id": self._session_id},
                        timeout=5,
                    )
                except Exception:
                    pass

        finally:
            self._secure_data.clear_all()
            self._session_id = ""
            self._status = ConnectionStatus.DISCONNECTED
            self._permission_level = PermissionLevel.NONE
            self._connected_at = None
            self._log("Disconnected and cleaned up")

    def __enter__(self) -> "ClawdbotConnector":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()

    def _send_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        timeout: int = REQUEST_TIMEOUT,
    ) -> Optional[Dict[str, Any]]:
        url = f"http://{self._host}:{self._port}{endpoint}"

        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            response = urllib.request.urlopen(request, timeout=timeout)
            return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise
        except urllib.error.URLError:
            return None

    def _create_signature(self, data: str) -> str:
        key = f"clawd4dummies:{self._session_id}".encode("utf-8")
        message = data.encode("utf-8")
        signature = hmac.new(key, message, hashlib.sha256)
        return signature.hexdigest()

    def _log(self, message: str) -> None:
        if self._verbose:
            print(f"[ClawdbotConnector] {message}")


def create_connector(
    host: str = ClawdbotConnector.DEFAULT_HOST,
    port: int = ClawdbotConnector.DEFAULT_PORT,
    verbose: bool = False,
) -> ClawdbotConnector:
    return ClawdbotConnector(host=host, port=port, verbose=verbose)
