"""
Abstract base class for all security scanner modules.
"""

from abc import ABC, abstractmethod
from typing import List

from clawd_for_dummies.models.finding import Finding
from clawd_for_dummies.models.system_info import SystemInfo


class BaseScanner(ABC):
    """Base class for security scanners."""

    def __init__(self, system_info: SystemInfo, verbose: bool = False):
        self.system_info = system_info
        self.verbose = verbose
        self.findings: List[Finding] = []

    @abstractmethod
    def scan(self) -> List[Finding]:
        pass

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        pass

    def add_finding(self, finding: Finding) -> None:
        self.findings.append(finding)

    def log(self, message: str) -> None:
        if self.verbose:
            print(f"  [{self.get_name()}] {message}")
