"""
Tests for data models.
"""

import pytest
from datetime import datetime

from clawd_for_dummies.models.finding import Finding, Severity, Category
from clawd_for_dummies.models.scan_result import ScanResult, RiskLevel
from clawd_for_dummies.models.system_info import SystemInfo


class TestFinding:
    """Tests for the Finding model."""

    def test_finding_creation(self):
        """Test creating a finding."""
        finding = Finding(
            id="TEST-001",
            title="Test Finding",
            description="This is a test finding",
            severity=Severity.HIGH,
            category=Category.PORT,
            cvss_score=7.5,
        )

        assert finding.id == "TEST-001"
        assert finding.title == "Test Finding"
        assert finding.severity == Severity.HIGH
        assert finding.cvss_score == 7.5

    def test_finding_validation(self):
        """Test finding validation."""
        with pytest.raises(ValueError):
            Finding(
                id="",
                title="Test",
                description="Test",
                severity=Severity.LOW,
                category=Category.CONFIG,
            )

        with pytest.raises(ValueError):
            Finding(
                id="TEST",
                title="",
                description="Test",
                severity=Severity.LOW,
                category=Category.CONFIG,
            )

    def test_severity_properties(self):
        """Test severity properties."""
        assert Severity.CRITICAL.color == "red"
        assert Severity.HIGH.indicator == "[H]"
        assert Severity.MEDIUM.description == "Fix within 1 week - Moderate risk"

    def test_finding_to_dict(self):
        """Test converting finding to dictionary."""
        finding = Finding(
            id="TEST-001",
            title="Test",
            description="Test description",
            severity=Severity.LOW,
            category=Category.CONFIG,
        )

        data = finding.to_dict()
        assert data["id"] == "TEST-001"
        assert data["severity"] == "low"
        assert data["category"] == "config"


class TestScanResult:
    """Tests for the ScanResult model."""

    def test_scan_result_creation(self):
        """Test creating a scan result."""
        system_info = SystemInfo()

        result = ScanResult(
            scan_id="test-123",
            timestamp=datetime.now(),
            duration_seconds=5.0,
            system_info=system_info,
            findings=[],
        )

        assert result.scan_id == "test-123"
        assert result.duration_seconds == 5.0
        assert result.risk_level == RiskLevel.SAFE

    def test_risk_calculation(self):
        """Test risk score calculation."""
        system_info = SystemInfo()

        finding = Finding(
            id="TEST-001",
            title="Critical Test",
            description="Test",
            severity=Severity.CRITICAL,
            category=Category.PORT,
            cvss_score=9.5,
        )

        result = ScanResult(
            scan_id="test-123",
            timestamp=datetime.now(),
            duration_seconds=1.0,
            system_info=system_info,
            findings=[finding],
        )

        assert result.critical_count == 1
        assert result.risk_level == RiskLevel.CRITICAL
        assert result.overall_risk_score > 0


class TestSystemInfo:
    """Tests for the SystemInfo model."""

    def test_system_info_creation(self):
        """Test creating system info."""
        info = SystemInfo(
            hostname="test-host",
            os_name="Linux",
            python_version="3.9.0",
        )

        assert info.hostname == "test-host"
        assert info.os_name == "Linux"
        assert info.python_version == "3.9.0"

    def test_platform_detection(self):
        """Test platform detection methods."""
        windows_info = SystemInfo(os_name="Windows")
        assert windows_info.is_windows is True
        assert windows_info.is_linux is False
        assert windows_info.is_macos is False

        linux_info = SystemInfo(os_name="Linux")
        assert linux_info.is_linux is True

        mac_info = SystemInfo(os_name="Darwin")
        assert mac_info.is_macos is True

    def test_system_info_collection(self):
        """Test system info auto-collection."""
        info = SystemInfo.collect()

        assert info.hostname != ""
        assert info.os_name != ""
        assert info.python_version != ""
