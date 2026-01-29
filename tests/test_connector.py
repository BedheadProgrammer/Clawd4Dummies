"""
Tests for the Clawdbot connector module.
"""

from datetime import datetime
from unittest.mock import Mock, patch

from clawd_for_dummies.connector import (
    ClawdbotConnector,
    ConnectionStatus,
    PermissionLevel,
    HandshakeResult,
    SecurityCheckRequest,
    SecurityCheckResponse,
    create_connector,
)


class TestConnectionStatus:
    """Tests for ConnectionStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert ConnectionStatus.DISCONNECTED.value == "disconnected"
        assert ConnectionStatus.CONNECTING.value == "connecting"
        assert ConnectionStatus.AWAITING_PERMISSION.value == "awaiting_permission"
        assert ConnectionStatus.CONNECTED.value == "connected"
        assert ConnectionStatus.AUTHENTICATED.value == "authenticated"
        assert ConnectionStatus.ERROR.value == "error"

    def test_str_conversion(self):
        """Test string conversion."""
        assert str(ConnectionStatus.CONNECTED) == "connected"


class TestPermissionLevel:
    """Tests for PermissionLevel enum."""

    def test_permission_values(self):
        """Test all permission levels exist."""
        assert PermissionLevel.NONE.value == "none"
        assert PermissionLevel.READ_ONLY.value == "read_only"
        assert PermissionLevel.SCAN.value == "scan"
        assert PermissionLevel.FULL.value == "full"


class TestHandshakeResult:
    """Tests for HandshakeResult dataclass."""

    def test_creation(self):
        """Test creating a HandshakeResult."""
        result = HandshakeResult(
            success=True,
            status=ConnectionStatus.AUTHENTICATED,
            permission_level=PermissionLevel.SCAN,
            session_id="test-session-123",
            clawdbot_version="1.0.0",
            message="Connected successfully",
        )

        assert result.success is True
        assert result.status == ConnectionStatus.AUTHENTICATED
        assert result.permission_level == PermissionLevel.SCAN
        assert result.session_id == "test-session-123"

    def test_to_dict(self):
        """Test converting to dictionary."""
        result = HandshakeResult(
            success=True,
            status=ConnectionStatus.CONNECTED,
        )

        data = result.to_dict()
        assert data["success"] is True
        assert data["status"] == "connected"
        assert "timestamp" in data

    def test_error_result(self):
        """Test creating an error result."""
        result = HandshakeResult(
            success=False,
            status=ConnectionStatus.ERROR,
            error="Connection refused",
        )

        assert result.success is False
        assert result.error == "Connection refused"


class TestSecurityCheckRequest:
    """Tests for SecurityCheckRequest dataclass."""

    def test_creation(self):
        """Test creating a request."""
        request = SecurityCheckRequest(
            check_type="authentication",
            parameters={"strict": True},
            session_id="session-123",
        )

        assert request.check_type == "authentication"
        assert request.parameters["strict"] is True
        assert request.session_id == "session-123"
        assert isinstance(request.timestamp, datetime)


class TestSecurityCheckResponse:
    """Tests for SecurityCheckResponse dataclass."""

    def test_success_response(self):
        """Test creating a success response."""
        response = SecurityCheckResponse(
            check_type="authentication",
            success=True,
            result={"enabled": True},
            findings=[],
        )

        assert response.success is True
        assert response.result["enabled"] is True
        assert len(response.findings) == 0

    def test_failure_response(self):
        """Test creating a failure response."""
        response = SecurityCheckResponse(
            check_type="sandbox",
            success=False,
            error="Sandbox not enabled",
        )

        assert response.success is False
        assert response.error == "Sandbox not enabled"


class TestClawdbotConnector:
    """Tests for ClawdbotConnector class."""

    def test_initialization(self):
        """Test connector initialization."""
        connector = ClawdbotConnector()

        assert connector.host == "127.0.0.1"
        assert connector.port == 18789
        assert connector.status == ConnectionStatus.DISCONNECTED
        assert connector.permission_level == PermissionLevel.NONE
        assert connector.is_connected is False

    def test_custom_host_port(self):
        """Test connector with custom host/port."""
        connector = ClawdbotConnector(host="192.168.1.100", port=9999)

        assert connector.host == "192.168.1.100"
        assert connector.port == 9999

    def test_is_connected_property(self):
        """Test is_connected property."""
        connector = ClawdbotConnector()
        assert connector.is_connected is False

        connector._status = ConnectionStatus.CONNECTED
        assert connector.is_connected is True

        connector._status = ConnectionStatus.AUTHENTICATED
        assert connector.is_connected is True

        connector._status = ConnectionStatus.ERROR
        assert connector.is_connected is False

    def test_permission_callback(self):
        """Test setting permission callback."""
        connector = ClawdbotConnector()

        callback = Mock(return_value=True)
        connector.set_permission_callback(callback)

        assert connector._permission_callback is callback

    @patch("socket.socket")
    def test_discover_when_running(self, mock_socket_class):
        """Test discovering Clawdbot when it's running."""
        mock_socket = Mock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket

        connector = ClawdbotConnector()
        result = connector.discover()

        assert result is True
        mock_socket.connect_ex.assert_called_once()
        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    def test_discover_when_not_running(self, mock_socket_class):
        """Test discovering Clawdbot when it's not running."""
        mock_socket = Mock()
        mock_socket.connect_ex.return_value = 1  # Connection refused
        mock_socket_class.return_value = mock_socket

        connector = ClawdbotConnector()
        result = connector.discover()

        assert result is False

    @patch("socket.socket")
    def test_discover_socket_error(self, mock_socket_class):
        """Test discovering Clawdbot with socket error."""
        mock_socket_class.side_effect = OSError("Network error")

        connector = ClawdbotConnector(verbose=True)
        result = connector.discover()

        assert result is False

    def test_disconnect_clears_data(self):
        """Test that disconnect clears sensitive data."""
        connector = ClawdbotConnector()
        connector._session_id = "test-session"
        connector._status = ConnectionStatus.CONNECTED
        connector._permission_level = PermissionLevel.SCAN
        connector._secure_data.set("token", "secret123", sensitive=True)

        connector.disconnect()

        assert connector._session_id == ""
        assert connector.status == ConnectionStatus.DISCONNECTED
        assert connector.permission_level == PermissionLevel.NONE

    def test_context_manager(self):
        """Test connector as context manager."""
        with ClawdbotConnector() as connector:
            connector._status = ConnectionStatus.CONNECTED
            connector._session_id = "test"

        assert connector.status == ConnectionStatus.DISCONNECTED
        assert connector._session_id == ""

    @patch.object(ClawdbotConnector, "discover", return_value=False)
    def test_handshake_no_clawdbot(self, mock_discover):
        """Test handshake when Clawdbot is not running."""
        connector = ClawdbotConnector()
        result = connector.handshake()

        assert result.success is False
        assert result.status == ConnectionStatus.ERROR
        assert "not detected" in result.error.lower()

    @patch.object(ClawdbotConnector, "discover", return_value=True)
    @patch.object(ClawdbotConnector, "_send_request")
    def test_handshake_with_callback_denied(self, mock_send, mock_discover):
        """Test handshake when permission is denied via callback."""
        connector = ClawdbotConnector()
        connector.set_permission_callback(lambda msg: False)

        result = connector.handshake()

        assert result.success is False
        assert result.status == ConnectionStatus.DISCONNECTED
        assert "denied" in result.message.lower()

    @patch.object(ClawdbotConnector, "discover", return_value=True)
    @patch.object(ClawdbotConnector, "_send_request")
    def test_handshake_success(self, mock_send, mock_discover):
        """Test successful handshake."""
        mock_send.return_value = {
            "success": True,
            "granted_permission": "scan",
            "version": "2.0.0",
        }

        connector = ClawdbotConnector()
        connector.set_permission_callback(lambda msg: True)

        result = connector.handshake()

        assert result.success is True
        assert result.status == ConnectionStatus.AUTHENTICATED
        assert result.permission_level == PermissionLevel.SCAN
        assert result.clawdbot_version == "2.0.0"

    def test_request_security_check_not_connected(self):
        """Test security check when not connected."""
        connector = ClawdbotConnector()

        response = connector.request_security_check("authentication")

        assert response.success is False
        assert "not connected" in response.error.lower()

    def test_request_security_check_no_permission(self):
        """Test security check with no permission."""
        connector = ClawdbotConnector()
        connector._status = ConnectionStatus.CONNECTED
        connector._permission_level = PermissionLevel.NONE

        response = connector.request_security_check("authentication")

        assert response.success is False
        assert "no permission" in response.error.lower()


class TestCreateConnector:
    """Tests for create_connector factory function."""

    def test_default_creation(self):
        """Test creating connector with defaults."""
        connector = create_connector()

        assert connector.host == "127.0.0.1"
        assert connector.port == 18789

    def test_custom_creation(self):
        """Test creating connector with custom values."""
        connector = create_connector(
            host="10.0.0.1", port=9000, verbose=True
        )

        assert connector.host == "10.0.0.1"
        assert connector.port == 9000
        assert connector._verbose is True
