"""
System information model for collecting host environment details.
"""

import platform
import socket
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class SystemInfo:
    """System information collected during security scans."""

    hostname: str = ""
    os_name: str = ""
    os_version: str = ""
    os_release: str = ""
    architecture: str = ""
    processor: str = ""
    python_version: str = ""
    python_executable: str = ""
    is_admin: bool = False
    username: str = ""
    home_directory: str = ""
    public_ip: Optional[str] = None
    local_ips: List[str] = field(default_factory=list)
    network_interfaces: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.hostname:
            self.hostname = socket.gethostname()
        if not self.os_name:
            self.os_name = platform.system()
        if not self.os_version:
            self.os_version = platform.version()
        if not self.os_release:
            self.os_release = platform.release()
        if not self.architecture:
            self.architecture = platform.machine()
        if not self.processor:
            self.processor = platform.processor()
        if not self.python_version:
            self.python_version = platform.python_version()

    @property
    def is_windows(self) -> bool:
        return self.os_name.lower() == "windows"

    @property
    def is_macos(self) -> bool:
        return self.os_name.lower() == "darwin"

    @property
    def is_linux(self) -> bool:
        return self.os_name.lower() == "linux"

    @property
    def platform_display(self) -> str:
        if self.is_windows:
            return f"Windows {self.os_release}"
        elif self.is_macos:
            return f"macOS {self.os_release}"
        elif self.is_linux:
            return f"Linux ({self.os_release})"
        else:
            return f"{self.os_name} {self.os_release}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hostname": self.hostname,
            "os_name": self.os_name,
            "os_version": self.os_version,
            "os_release": self.os_release,
            "architecture": self.architecture,
            "processor": self.processor,
            "python_version": self.python_version,
            "python_executable": self.python_executable,
            "is_admin": self.is_admin,
            "username": self.username,
            "home_directory": self.home_directory,
            "public_ip": self.public_ip,
            "local_ips": self.local_ips,
            "network_interfaces": self.network_interfaces,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemInfo":
        return cls(
            hostname=data.get("hostname", ""),
            os_name=data.get("os_name", ""),
            os_version=data.get("os_version", ""),
            os_release=data.get("os_release", ""),
            architecture=data.get("architecture", ""),
            processor=data.get("processor", ""),
            python_version=data.get("python_version", ""),
            python_executable=data.get("python_executable", ""),
            is_admin=data.get("is_admin", False),
            username=data.get("username", ""),
            home_directory=data.get("home_directory", ""),
            public_ip=data.get("public_ip"),
            local_ips=data.get("local_ips", []),
            network_interfaces=data.get("network_interfaces", {}),
        )

    @classmethod
    def collect(cls) -> "SystemInfo":
        """Collect system information from the current system."""
        import getpass
        import os

        info = cls()

        try:
            info.username = getpass.getuser()
        except Exception:
            info.username = "unknown"

        info.home_directory = os.path.expanduser("~")
        info.is_admin = cls._check_admin_privileges()
        info.python_executable = os.sys.executable
        info.local_ips = cls._get_local_ips()

        return info

    @staticmethod
    def _check_admin_privileges() -> bool:
        import os

        try:
            if os.name == "nt":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False

    @staticmethod
    def _get_local_ips() -> List[str]:
        import socket

        ips = []
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if ip and ip != "127.0.0.1":
                ips.append(ip)
        except Exception:
            pass

        try:
            import psutil
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        if ip and not ip.startswith("127."):
                            ips.append(ip)
        except ImportError:
            pass

        return list(set(ips))

    def format_for_report(self) -> str:
        lines = [
            "SYSTEM INFORMATION:",
            f"  Hostname: {self.hostname}",
            f"  Platform: {self.platform_display}",
            f"  Architecture: {self.architecture}",
            f"  Python: {self.python_version}",
            f"  User: {self.username}",
            f"  Admin Privileges: {'Yes' if self.is_admin else 'No'}",
        ]

        if self.local_ips:
            lines.append(f"  Local IPs: {', '.join(self.local_ips)}")

        if self.public_ip:
            lines.append(f"  Public IP: {self.public_ip}")

        return "\n".join(lines)
