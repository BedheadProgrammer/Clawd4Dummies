"""
User interfaces for ClawdForDummies.

This module provides both CLI and GUI interfaces for the security scanner.

CLI:
    The CLI interface provides console-based output with color-coded
    severity levels and formatted scan results.

GUI:
    The GUI is built with React + Electron and provides a modern,
    visual interface. See the clawd-for-dummies-gui directory for
    the GUI implementation.
"""

from clawd_for_dummies.interface.cli import CLI

__all__ = ['CLI']
