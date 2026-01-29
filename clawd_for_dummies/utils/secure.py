"""
Secure data handling utilities for sensitive information management.
"""

import gc
import secrets
from typing import Any, Dict, Optional, Set, TypeVar, Generic
from contextlib import contextmanager
import ctypes

T = TypeVar("T")


class SecureString:
    """String wrapper that securely handles sensitive data with memory clearing."""

    __slots__ = ("_data", "_cleared")

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("SecureString requires a string value")
        self._data: bytes = value.encode("utf-8")
        self._cleared: bool = False

    def get_value(self) -> str:
        if self._cleared:
            raise ValueError("SecureString has been cleared")
        return self._data.decode("utf-8")

    def clear(self) -> None:
        if not self._cleared and self._data:
            length = len(self._data)
            try:
                self._overwrite_memory(self._data)
            except Exception:
                pass
            finally:
                self._data = b"\x00" * length
                self._cleared = True
                gc.collect()

    @staticmethod
    def _overwrite_memory(data: bytes) -> None:
        try:
            buffer = (ctypes.c_char * len(data)).from_buffer_copy(data)
            ctypes.memset(ctypes.addressof(buffer), 0, len(data))
        except Exception:
            pass

    def __del__(self) -> None:
        if hasattr(self, "_cleared"):
            self.clear()

    def __repr__(self) -> str:
        if self._cleared:
            return "SecureString(<cleared>)"
        return "SecureString(<hidden>)"

    def __str__(self) -> str:
        return "SecureString(<hidden>)"

    def __len__(self) -> int:
        if self._cleared:
            return 0
        return len(self._data)

    def __bool__(self) -> bool:
        return not self._cleared and len(self._data) > 0


class SecureData(Generic[T]):
    """Generic wrapper for sensitive data with lifecycle management."""

    __slots__ = ("_value", "_cleared")

    def __init__(self, value: T) -> None:
        self._value: Optional[T] = value
        self._cleared: bool = False

    def get(self) -> T:
        if self._cleared or self._value is None:
            raise ValueError("SecureData has been cleared or is empty")
        return self._value

    def clear(self) -> None:
        self._value = None
        self._cleared = True
        gc.collect()

    def __repr__(self) -> str:
        if self._cleared:
            return "SecureData(<cleared>)"
        return "SecureData(<hidden>)"


def mask_credential(credential: str, visible_chars: int = 4) -> str:
    """Mask a credential for safe display."""
    if not credential:
        return ""

    if len(credential) <= visible_chars * 2:
        return "*" * len(credential)

    return (
        credential[:visible_chars]
        + "*" * (len(credential) - visible_chars * 2)
        + credential[-visible_chars:]
    )


def sanitize_string(value: str) -> str:
    """Remove null bytes and control characters from a string."""
    if not isinstance(value, str):
        return str(value)

    sanitized = ""
    for char in value:
        code = ord(char)
        if code == 0:
            continue
        if code < 32 and char not in "\n\r\t":
            continue
        if code == 127:
            continue
        sanitized += char

    return sanitized


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


@contextmanager
def secure_file_access(filepath: str, mode: str = "r", encoding: str = "utf-8"):
    """Context manager for secure file access with cleanup."""
    file_handle = None
    try:
        if "b" in mode:
            file_handle = open(filepath, mode)
        else:
            file_handle = open(filepath, mode, encoding=encoding)
        yield file_handle
    finally:
        if file_handle:
            file_handle.close()
        gc.collect()


class SecureDict:
    """Dictionary that securely handles sensitive values."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}
        self._sensitive_keys: Set[str] = set()

    def set(self, key: str, value: Any, sensitive: bool = False) -> None:
        if sensitive:
            if isinstance(value, str):
                self._data[key] = SecureString(value)
            else:
                self._data[key] = SecureData(value)
            self._sensitive_keys.add(key)
        else:
            self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        value = self._data.get(key, default)
        if isinstance(value, (SecureString, SecureData)):
            try:
                if isinstance(value, SecureString):
                    return value.get_value()
                return value.get()
            except ValueError:
                return default
        return value

    def clear_sensitive(self) -> None:
        for key in list(self._sensitive_keys):
            if key in self._data:
                value = self._data[key]
                if hasattr(value, "clear"):
                    value.clear()
                del self._data[key]
        self._sensitive_keys.clear()
        gc.collect()

    def clear_all(self) -> None:
        self.clear_sensitive()
        self._data.clear()
        gc.collect()

    def __repr__(self) -> str:
        visible_keys = [k for k in self._data.keys() if k not in self._sensitive_keys]
        hidden_count = len(self._sensitive_keys)
        return f"SecureDict({visible_keys}, hidden={hidden_count})"


def validate_type(value: Any, expected_type: type, name: str = "value") -> None:
    """Validate that a value has the expected type."""
    if not isinstance(value, expected_type):
        raise TypeError(
            f"{name} must be of type {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )


def validate_non_empty_string(value: Any, name: str = "value") -> str:
    """Validate that a value is a non-empty string."""
    validate_type(value, str, name)
    if not value.strip():
        raise ValueError(f"{name} cannot be empty")
    return value
