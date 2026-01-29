"""
Scanner orchestrator that coordinates security scanning modules.
"""

import time
import uuid
from datetime import datetime
from typing import List, Optional, Type

from clawd_for_dummies.models.finding import Finding
from clawd_for_dummies.models.scan_result import ScanResult
from clawd_for_dummies.models.system_info import SystemInfo
from clawd_for_dummies.engine.base_scanner import BaseScanner
from clawd_for_dummies.engine.port_scanner import PortScanner
from clawd_for_dummies.engine.credential_scanner import CredentialScanner
from clawd_for_dummies.engine.config_analyzer import ConfigAnalyzer
from clawd_for_dummies.engine.process_monitor import ProcessMonitor
from clawd_for_dummies.engine.file_permission_checker import (
    FilePermissionChecker,
)
from clawd_for_dummies.engine.network_analyzer import NetworkAnalyzer
from clawd_for_dummies.engine.clawdbot_security_scanner import (
    ClawdbotSecurityScanner,
)


class SecurityScanner:
    """Orchestrates all security scanning modules."""

    SCANNER_REGISTRY: dict[str, Type[BaseScanner]] = {
        "port": PortScanner,
        "credential": CredentialScanner,
        "config": ConfigAnalyzer,
        "process": ProcessMonitor,
        "permission": FilePermissionChecker,
        "network": NetworkAnalyzer,
        "clawdbot": ClawdbotSecurityScanner,
    }

    def __init__(
        self,
        modules: Optional[List[str]] = None,
        system_info: Optional[SystemInfo] = None,
        verbose: bool = False,
    ):
        self.modules = modules or list(self.SCANNER_REGISTRY.keys())
        self.system_info = system_info or SystemInfo.collect()
        self.verbose = verbose
        self.findings: List[Finding] = []

    def run(self) -> ScanResult:
        start_time = time.time()
        scan_id = str(uuid.uuid4())[:8]

        self.findings = []

        for module_name in self.modules:
            if module_name not in self.SCANNER_REGISTRY:
                if self.verbose:
                    print(f"Warning: Unknown module '{module_name}', skipping")
                continue

            scanner_class = self.SCANNER_REGISTRY[module_name]
            scanner = scanner_class(self.system_info, self.verbose)

            try:
                if self.verbose:
                    print(f"Running {scanner.get_name()}...")

                module_findings = scanner.scan()
                self.findings.extend(module_findings)

                if self.verbose:
                    print(f"  Found {len(module_findings)} issues")

            except Exception as e:
                if self.verbose:
                    print(f"  Error: {e}")

        duration = time.time() - start_time

        return ScanResult(
            scan_id=scan_id,
            timestamp=datetime.now(),
            duration_seconds=duration,
            system_info=self.system_info,
            findings=self.findings,
        )

    @classmethod
    def list_available_modules(cls) -> List[str]:
        return list(cls.SCANNER_REGISTRY.keys())

    @classmethod
    def get_module_description(cls, module_name: str) -> str:
        if module_name not in cls.SCANNER_REGISTRY:
            return "Unknown module"

        scanner_class = cls.SCANNER_REGISTRY[module_name]
        return scanner_class.get_description()
