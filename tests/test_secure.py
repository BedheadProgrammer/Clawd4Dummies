"""
Tests for secure data handling utilities.
"""

import os
import tempfile
import pytest

from clawd_for_dummies.utils.secure import (
    SecureString,
    SecureData,
    SecureDict,
    mask_credential,
    sanitize_string,
    generate_secure_token,
    secure_file_access,
    validate_type,
    validate_non_empty_string,
)


class TestSecureString:
    """Tests for SecureString class."""

    def test_creation(self):
        """Test creating a SecureString."""
        secret = SecureString("my_secret_password")
        assert len(secret) == len("my_secret_password".encode("utf-8"))
        assert bool(secret) is True

    def test_get_value(self):
        """Test retrieving the value."""
        secret = SecureString("my_secret")
        assert secret.get_value() == "my_secret"

    def test_clear(self):
        """Test clearing sensitive data."""
        secret = SecureString("my_secret")
        secret.clear()
        assert len(secret) == 0
        assert bool(secret) is False
        with pytest.raises(ValueError):
            secret.get_value()

    def test_repr_hides_value(self):
        """Test that repr doesn't expose the value."""
        secret = SecureString("my_secret")
        assert "my_secret" not in repr(secret)
        assert "hidden" in repr(secret).lower()

    def test_str_hides_value(self):
        """Test that str doesn't expose the value."""
        secret = SecureString("my_secret")
        assert "my_secret" not in str(secret)
        assert "hidden" in str(secret).lower()

    def test_type_error_on_non_string(self):
        """Test that non-string values raise TypeError."""
        with pytest.raises(TypeError):
            SecureString(12345)  # type: ignore

        with pytest.raises(TypeError):
            SecureString(None)  # type: ignore


class TestSecureData:
    """Tests for SecureData class."""

    def test_creation_and_get(self):
        """Test creating and getting data."""
        data = SecureData({"key": "value"})
        assert data.get() == {"key": "value"}

    def test_clear(self):
        """Test clearing data."""
        data = SecureData("sensitive_data")
        data.clear()
        with pytest.raises(ValueError):
            data.get()

    def test_repr_hides_value(self):
        """Test that repr doesn't expose the value."""
        data = SecureData("sensitive")
        assert "sensitive" not in repr(data)


class TestSecureDict:
    """Tests for SecureDict class."""

    def test_set_and_get_regular(self):
        """Test setting and getting regular values."""
        d = SecureDict()
        d.set("key", "value")
        assert d.get("key") == "value"

    def test_set_and_get_sensitive(self):
        """Test setting and getting sensitive values."""
        d = SecureDict()
        d.set("password", "secret123", sensitive=True)
        assert d.get("password") == "secret123"

    def test_clear_sensitive(self):
        """Test clearing sensitive data only."""
        d = SecureDict()
        d.set("regular", "value1")
        d.set("sensitive", "value2", sensitive=True)

        d.clear_sensitive()

        assert d.get("regular") == "value1"
        assert d.get("sensitive") is None

    def test_clear_all(self):
        """Test clearing all data."""
        d = SecureDict()
        d.set("key1", "value1")
        d.set("key2", "value2", sensitive=True)

        d.clear_all()

        assert d.get("key1") is None
        assert d.get("key2") is None

    def test_repr_hides_sensitive(self):
        """Test that repr shows hidden count."""
        d = SecureDict()
        d.set("visible", "value")
        d.set("hidden", "secret", sensitive=True)

        repr_str = repr(d)
        assert "hidden=1" in repr_str


class TestMaskCredential:
    """Tests for mask_credential function."""

    def test_mask_long_credential(self):
        """Test masking a long credential."""
        masked = mask_credential("sk-ant-api03-1234567890abcdef")
        assert masked.startswith("sk-a")
        assert masked.endswith("cdef")
        assert "*" in masked

    def test_mask_short_credential(self):
        """Test masking a short credential."""
        masked = mask_credential("short")
        assert masked == "*****"

    def test_mask_empty_credential(self):
        """Test masking empty credential."""
        assert mask_credential("") == ""

    def test_custom_visible_chars(self):
        """Test custom visible character count."""
        masked = mask_credential("1234567890", visible_chars=2)
        assert masked.startswith("12")
        assert masked.endswith("90")


class TestSanitizeString:
    """Tests for sanitize_string function."""

    def test_removes_null_bytes(self):
        """Test removal of null bytes."""
        result = sanitize_string("hello\x00world")
        assert result == "helloworld"
        assert "\x00" not in result

    def test_removes_control_characters(self):
        """Test removal of control characters."""
        result = sanitize_string("hello\x01\x02world")
        assert result == "helloworld"

    def test_preserves_newlines_and_tabs(self):
        """Test that newlines and tabs are preserved."""
        result = sanitize_string("hello\nworld\there")
        assert result == "hello\nworld\there"

    def test_handles_non_string(self):
        """Test handling of non-string input."""
        result = sanitize_string(12345)
        assert result == "12345"


class TestGenerateSecureToken:
    """Tests for generate_secure_token function."""

    def test_default_length(self):
        """Test default token generation."""
        token = generate_secure_token()
        assert len(token) > 20  # URL-safe base64 is ~4/3 of byte length

    def test_custom_length(self):
        """Test custom length token."""
        token16 = generate_secure_token(16)
        token64 = generate_secure_token(64)
        assert len(token64) > len(token16)

    def test_tokens_are_unique(self):
        """Test that tokens are unique."""
        tokens = [generate_secure_token() for _ in range(100)]
        assert len(set(tokens)) == 100


class TestValidateType:
    """Tests for validate_type function."""

    def test_valid_type(self):
        """Test validation passes for correct type."""
        validate_type("hello", str)
        validate_type(123, int)
        validate_type([1, 2], list)

    def test_invalid_type(self):
        """Test validation fails for wrong type."""
        with pytest.raises(TypeError) as exc_info:
            validate_type("hello", int, "my_value")
        assert "my_value" in str(exc_info.value)
        assert "int" in str(exc_info.value)
        assert "str" in str(exc_info.value)


class TestValidateNonEmptyString:
    """Tests for validate_non_empty_string function."""

    def test_valid_string(self):
        """Test validation passes for non-empty string."""
        result = validate_non_empty_string("hello")
        assert result == "hello"

    def test_empty_string_fails(self):
        """Test validation fails for empty string."""
        with pytest.raises(ValueError):
            validate_non_empty_string("")

    def test_whitespace_only_fails(self):
        """Test validation fails for whitespace-only string."""
        with pytest.raises(ValueError):
            validate_non_empty_string("   ")

    def test_non_string_fails(self):
        """Test validation fails for non-string."""
        with pytest.raises(TypeError):
            validate_non_empty_string(123)  # type: ignore


class TestSecureFileAccess:
    """Tests for secure_file_access context manager."""

    def test_read_file(self):
        """Test reading a file with secure access."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            with secure_file_access(temp_path, "r") as f:
                content = f.read()
            assert content == "test content"
        finally:
            os.unlink(temp_path)

    def test_write_file(self):
        """Test writing a file with secure access."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            temp_path = f.name

        try:
            with secure_file_access(temp_path, "w") as f:
                f.write("secure content")

            with open(temp_path, "r") as f:
                assert f.read() == "secure content"
        finally:
            os.unlink(temp_path)

    def test_binary_mode(self):
        """Test binary mode file access."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
            f.write(b"binary data")
            temp_path = f.name

        try:
            with secure_file_access(temp_path, "rb") as f:
                content = f.read()
            assert content == b"binary data"
        finally:
            os.unlink(temp_path)

    def test_file_closed_after_context(self):
        """Test that file is properly closed after context exits."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            with secure_file_access(temp_path, "r") as f:
                pass
            assert f.closed
        finally:
            os.unlink(temp_path)

    def test_file_closed_on_exception(self):
        """Test that file is closed even if exception occurs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test")
            temp_path = f.name

        file_handle = None
        try:
            try:
                with secure_file_access(temp_path, "r") as f:
                    file_handle = f
                    raise ValueError("Intentional error")
            except ValueError:
                pass  # Expected
            assert file_handle.closed
        finally:
            os.unlink(temp_path)
