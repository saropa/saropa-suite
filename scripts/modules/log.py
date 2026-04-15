"""
Dual-output logging — colored terminal + plain-text log file.

All output functions write to both stdout (with ANSI color) and a
persistent log file under reports/<yyyymmdd>/<datetime>_publish.log.
The log file receives stripped plain text so it is readable in any editor.
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from scripts.modules.color import bold, cyan, dim, green, red, yellow


# --------------------------------------------------------------------------- #
# Module state
# --------------------------------------------------------------------------- #

# Populated by init_log_file() before any output.
_log_file_handle = None
_log_file_path: Path | None = None

# Regex to strip ANSI escapes for the plain-text log file
_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


# --------------------------------------------------------------------------- #
# Log file lifecycle
# --------------------------------------------------------------------------- #

def init_log_file(reports_dir: Path) -> Path:
    """Create the log directory and open the log file.  Returns the log path."""
    global _log_file_handle, _log_file_path

    now = datetime.now()
    date_dir = now.strftime("%Y%m%d")
    filename = now.strftime("%Y%m%d_%H%M%S") + "_publish.log"

    log_dir = reports_dir / date_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    _log_file_path = log_dir / filename
    _log_file_handle = open(_log_file_path, "w", encoding="utf-8")

    # Write a header so the log file is self-describing
    _log_file_handle.write("Saropa Suite — publish log\n")
    _log_file_handle.write(f"Started: {now.isoformat()}\n")
    _log_file_handle.write(f"{'=' * 60}\n\n")
    _log_file_handle.flush()
    return _log_file_path


def close_log_file() -> None:
    """Flush a footer and close the log file."""
    global _log_file_handle
    if _log_file_handle is not None:
        now = datetime.now()
        _log_file_handle.write(f"\n{'=' * 60}\n")
        _log_file_handle.write(f"Finished: {now.isoformat()}\n")
        _log_file_handle.close()
        _log_file_handle = None


# --------------------------------------------------------------------------- #
# Core write helpers
# --------------------------------------------------------------------------- #

def write_log(line: str) -> None:
    """Append a plain-text line to the log file (no terminal output)."""
    if _log_file_handle is not None:
        _log_file_handle.write(_strip_ansi(line) + "\n")
        _log_file_handle.flush()


def print_and_log(line: str, *, file=None) -> None:
    """Print to terminal and append to log file."""
    print(line, file=file or sys.stdout)
    write_log(line)


# --------------------------------------------------------------------------- #
# Semantic output functions
# --------------------------------------------------------------------------- #

def fatal(message: str) -> None:
    """Print an error message, log it, and exit with a non-zero status."""
    line = f"\n  {red('ERROR:')} {message}\n"
    print_and_log(line, file=sys.stderr)
    close_log_file()
    sys.exit(1)


def warn(message: str) -> None:
    """Print a yellow warning."""
    print_and_log(f"  {yellow('WARNING:')} {message}")


def success(message: str) -> None:
    """Print a green success confirmation."""
    print_and_log(f"  {green('OK:')} {message}")


def info(message: str) -> None:
    """Print a neutral informational line."""
    print_and_log(f"  {message}")


def detail(message: str) -> None:
    """Print a dimmed detail line — less prominent than info."""
    print_and_log(f"  {dim(message)}")


def heading(message: str) -> None:
    """Print a prominent section heading with colored bars."""
    bar = "=" * 60
    print_and_log(f"\n{cyan(bar)}")
    print_and_log(f"  {bold(message)}")
    print_and_log(f"{cyan(bar)}")


# --------------------------------------------------------------------------- #
# Subprocess runner
# --------------------------------------------------------------------------- #

def run(cmd: list[str], *, cwd: Path, check: bool = True,
        capture: bool = False) -> subprocess.CompletedProcess:
    """Run a subprocess, echoing the command and logging output.

    Uses shell=True on Windows because tools like vsce are .cmd scripts
    that cannot be invoked directly by CreateProcess.
    """
    display_cmd = " ".join(cmd)
    print_and_log(f"  {dim('$')} {dim(display_cmd)}")

    result = subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        text=True,
        capture_output=capture,
        shell=(sys.platform == "win32"),
    )

    # Log captured stdout/stderr so the log file has full subprocess output
    if capture:
        if result.stdout and result.stdout.strip():
            for stdout_line in result.stdout.strip().splitlines():
                write_log(f"    [stdout] {stdout_line}")
        if result.stderr and result.stderr.strip():
            for stderr_line in result.stderr.strip().splitlines():
                write_log(f"    [stderr] {stderr_line}")

    return result


# --------------------------------------------------------------------------- #
# Interactive prompt
# --------------------------------------------------------------------------- #

def confirm(prompt: str) -> bool:
    """Ask the user a yes/no question.  Returns True on 'y'."""
    styled = f"\n  {yellow('?')} {bold(prompt)} {dim('[y/N]')} "
    answer = input(styled).strip().lower()
    # Log the question and the user's answer
    write_log(f"  ? {prompt} [y/N] -> {answer}")
    return answer == "y"
