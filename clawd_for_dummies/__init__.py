"""
Security scanner for Clawdbot/Moltbot deployments.
"""

__version__ = "1.0.0"
__author__ = "ClawdForDummies Team"
__license__ = "MIT"

from clawd_for_dummies.models.finding import Finding, Severity, Category
from clawd_for_dummies.models.scan_result import ScanResult
from clawd_for_dummies.models.system_info import SystemInfo
from clawd_for_dummies.connector import (
    ClawdbotConnector,
    ConnectionStatus,
    PermissionLevel,
    HandshakeResult,
    create_connector,
)

__all__ = [
    "Finding",
    "Severity",
    "Category",
    "ScanResult",
    "SystemInfo",
    "ClawdbotConnector",
    "ConnectionStatus",
    "PermissionLevel",
    "HandshakeResult",
    "create_connector",
]
