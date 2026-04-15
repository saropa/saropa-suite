"""
ANSI color support with automatic terminal detection.

Colors are disabled when:
- stdout is not a terminal (e.g. piped to a file)
- the NO_COLOR environment variable is set (https://no-color.org/)

On Windows 10+, ANSI virtual terminal processing is enabled via
SetConsoleMode so colors work in cmd.exe and PowerShell.
"""

import os
import sys

# --------------------------------------------------------------------------- #
# Initialization
# --------------------------------------------------------------------------- #

_COLOR_ENABLED = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

# Enable ANSI escape processing on Windows 10+ terminals.  Without this,
# cmd.exe and older PowerShell versions print raw escape sequences instead
# of rendering colors.
if _COLOR_ENABLED and sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        # STD_OUTPUT_HANDLE = -11
        handle = kernel32.GetStdHandle(-11)
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        # If anything goes wrong, just disable color rather than crashing.
        # This can happen in unusual terminal emulators or CI environments.
        _COLOR_ENABLED = False


# --------------------------------------------------------------------------- #
# Color functions
# --------------------------------------------------------------------------- #

def _ansi(code: str, text: str) -> str:
    """Wrap text in an ANSI escape sequence if color is enabled."""
    if _COLOR_ENABLED:
        return f"\033[{code}m{text}\033[0m"
    return text


def red(text: str) -> str:
    """Bold red — used for errors and missing items."""
    return _ansi("1;31", text)


def green(text: str) -> str:
    """Bold green — used for success confirmations."""
    return _ansi("1;32", text)


def yellow(text: str) -> str:
    """Bold yellow — used for warnings and prompts."""
    return _ansi("1;33", text)


def cyan(text: str) -> str:
    """Bold cyan — used for section heading bars."""
    return _ansi("1;36", text)


def bold(text: str) -> str:
    """Bold white — used for emphasis on key values."""
    return _ansi("1", text)


def dim(text: str) -> str:
    """Dimmed text — used for commands and secondary details."""
    return _ansi("2", text)
