"""
Post-publish verification — poll Marketplace and Open VSX until live.

After a successful ``vsce publish`` / ``ovsx publish``, the new version
does not appear instantly.  This module polls both registries on a
fixed interval until the expected version is returned, giving the user
confidence that the release actually landed.
"""

import json
import time
from pathlib import Path

from scripts.modules.color import bold, dim
from scripts.modules.log import detail, heading, info, run, success, warn


# How often to poll, in seconds.
POLL_INTERVAL_SECONDS = 20

# Give up after this many seconds to avoid infinite loops if a registry
# is having a prolonged outage.
MAX_WAIT_SECONDS = 1800


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #

def poll_until_live(
    publisher: str,
    name: str,
    version: str,
    *,
    check_ovsx: bool,
    cwd: Path,
) -> None:
    """Poll registries until *version* is the published version.

    Checks the VS Code Marketplace (always) and Open VSX (if
    *check_ovsx* is True) every :data:`POLL_INTERVAL_SECONDS` seconds.
    Registries that already show the correct version are checked once
    and then skipped on subsequent iterations.

    Parameters
    ----------
    publisher:
        Marketplace publisher ID (e.g. ``"saropa"``).
    name:
        Extension name (e.g. ``"saropa-suite"``).
    version:
        The exact semver string we just published (e.g. ``"1.0.4"``).
    check_ovsx:
        Whether to also verify the Open VSX Registry.
    cwd:
        Working directory for subprocess calls (passed to ``vsce``).
    """
    heading("Verifying published version is live")

    ext_id = f"{publisher}.{name}"
    info(f"Expecting {bold(ext_id)} v{bold(version)}")
    info(
        f"Polling every {POLL_INTERVAL_SECONDS}s "
        f"(timeout {MAX_WAIT_SECONDS // 60}m) …"
    )

    marketplace_live = False
    ovsx_live = not check_ovsx  # If skipping Open VSX, mark as done

    start = time.monotonic()

    while True:
        elapsed = time.monotonic() - start

        # ---- Check VS Code Marketplace ----------------------------------- #
        if not marketplace_live:
            found = _check_marketplace(ext_id, version, cwd=cwd)
            if found:
                marketplace_live = True
                success(
                    f"VS Code Marketplace shows v{bold(version)} "
                    f"({_elapsed_str(elapsed)})"
                )

        # ---- Check Open VSX ---------------------------------------------- #
        if not ovsx_live:
            found = _check_openvsx(publisher, name, version)
            if found:
                ovsx_live = True
                success(
                    f"Open VSX shows v{bold(version)} "
                    f"({_elapsed_str(elapsed)})"
                )

        # ---- All done? --------------------------------------------------- #
        if marketplace_live and ovsx_live:
            return

        # ---- Timeout? ---------------------------------------------------- #
        if elapsed >= MAX_WAIT_SECONDS:
            # Not fatal — the publish itself already succeeded.  The
            # registries might just be slow to propagate.
            pending = _pending_names(marketplace_live, ovsx_live)
            warn(
                f"Timed out after {MAX_WAIT_SECONDS // 60}m waiting for "
                f"{pending} to show v{version}.\n"
                "  The publish succeeded — the registry may just be slow.\n"
                "  Check manually in a few minutes."
            )
            return

        # ---- Wait before next poll --------------------------------------- #
        pending = _pending_names(marketplace_live, ovsx_live)
        detail(
            f"Waiting for {pending} … "
            f"retrying in {POLL_INTERVAL_SECONDS}s "
            f"({_elapsed_str(elapsed)} elapsed)"
        )
        time.sleep(POLL_INTERVAL_SECONDS)


# --------------------------------------------------------------------------- #
# Registry checkers
# --------------------------------------------------------------------------- #

def _check_marketplace(ext_id: str, expected: str, *, cwd: Path) -> bool:
    """Return True if the Marketplace reports *expected* as the latest version.

    Uses ``vsce show <id> --json`` which returns a JSON blob whose
    ``versions[0].version`` field is the latest published version.
    """
    result = run(
        ["vsce", "show", ext_id, "--json"],
        cwd=cwd,
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        return False

    try:
        data = json.loads(result.stdout)
        # The JSON structure nests versions under "versions" array —
        # the first entry is the latest.  Fall back to top-level
        # "version" if the shape changes.
        versions = data.get("versions", [])
        if versions:
            live = versions[0].get("version", "")
        else:
            live = data.get("version", "")
        return live == expected
    except (json.JSONDecodeError, IndexError, TypeError):
        return False


def _check_openvsx(publisher: str, name: str, expected: str) -> bool:
    """Return True if Open VSX reports *expected* as the latest version.

    Hits the public REST API directly via curl so we don't depend on
    the ovsx CLI for a simple GET request.
    """
    import subprocess
    import sys

    url = f"https://open-vsx.org/api/{publisher}/{name}"
    try:
        result = subprocess.run(
            ["curl", "-sf", url],
            capture_output=True,
            text=True,
            timeout=10,
            shell=(sys.platform == "win32"),
        )
        if result.returncode != 0:
            return False
        data = json.loads(result.stdout)
        return data.get("version", "") == expected
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return False


# --------------------------------------------------------------------------- #
# Formatting helpers
# --------------------------------------------------------------------------- #

def _elapsed_str(seconds: float) -> str:
    """Format elapsed seconds as a human-readable string like '1m 23s'."""
    total = int(seconds)
    if total < 60:
        return f"{total}s"
    minutes, secs = divmod(total, 60)
    return f"{minutes}m {secs:02d}s"


def _pending_names(marketplace_live: bool, ovsx_live: bool) -> str:
    """Return a human-readable string of registries we're still waiting for."""
    pending = []
    if not marketplace_live:
        pending.append("VS Code Marketplace")
    if not ovsx_live:
        pending.append("Open VSX")
    return " and ".join(pending)
