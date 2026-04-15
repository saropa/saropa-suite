"""
PAT (Personal Access Token) validation for Marketplace and Open VSX.

Validates tokens early — before expensive packaging and publish steps.
Returns a status so the caller can decide whether to use CLI publish
or fall back to browser-based manual upload.
"""

import os
import sys
from pathlib import Path

from scripts.modules.color import bold, dim
from scripts.modules.log import detail, heading, info, run, success, warn


# --------------------------------------------------------------------------- #
# VS Code Marketplace (VSCE_PAT)
# --------------------------------------------------------------------------- #

def check_vsce_pat(publisher: str, *, cwd: Path) -> bool:
    """Check whether VSCE_PAT is set and has publish rights for *publisher*.

    Returns True if the token is valid, False if missing or invalid.
    Never fatals — the caller decides how to handle a False result
    (e.g. fall back to browser-based upload).
    """
    heading("Authenticate — VS Code Marketplace")

    pat = os.environ.get("VSCE_PAT", "").strip()
    if not pat:
        warn(
            "VSCE_PAT environment variable is not set.\n"
            "  CLI-based publish (vsce publish) will not be available.\n"
            "  The script will fall back to browser-based upload."
        )
        return False

    info(f"VSCE_PAT is set ({dim(_mask(pat))}). Verifying publish rights …")

    result = run(
        ["vsce", "verify-pat", publisher],
        cwd=cwd,
        capture=True,
        check=False,
    )

    if result.returncode != 0:
        # Extract the most useful line from stderr/stdout for context.
        output = (result.stderr or "") + (result.stdout or "")
        snippet = _first_nonempty_line(output)
        snippet_part = f"\n  vsce says: {snippet}" if snippet else ""
        warn(
            f"VSCE_PAT verification failed for publisher "
            f"\"{publisher}\".{snippet_part}\n"
            "  CLI-based publish (vsce publish) will not be available.\n"
            "  The script will fall back to browser-based upload."
        )
        return False

    success(f"VSCE_PAT is valid for publisher {bold(publisher)}.")
    return True


# --------------------------------------------------------------------------- #
# Open VSX (OVSX_PAT)
# --------------------------------------------------------------------------- #

def check_ovsx_pat() -> bool:
    """Check whether OVSX_PAT is set.

    Open VSX has no ``verify-pat`` equivalent, so we can only check
    that the environment variable exists.  Returns True if present,
    False if missing.
    """
    heading("Authenticate — Open VSX Registry")

    pat = os.environ.get("OVSX_PAT", "").strip()
    if not pat:
        warn(
            "OVSX_PAT environment variable is not set.\n"
            "  Open VSX publishing will be skipped.\n"
            "  To create a token: https://open-vsx.org → Settings → "
            "Access Tokens"
        )
        return False

    info(f"OVSX_PAT is set ({dim(_mask(pat))}).")
    # No server-side verification available — ovsx validates at publish
    # time.  We at least know the env var is present and non-empty.
    detail("(Open VSX does not support pre-publish token verification.)")
    success("OVSX_PAT is present.")
    return True


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _mask(token: str) -> str:
    """Return a masked representation of a token for safe logging.

    Shows only the first 4 and last 4 characters so the user can
    identify which token is in use without exposing the full secret.
    """
    if len(token) <= 12:
        return "****"
    return f"{token[:4]}…{token[-4:]}"


def _first_nonempty_line(text: str) -> str:
    """Return the first non-blank line from *text*, or empty string."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""
