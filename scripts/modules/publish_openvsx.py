"""
Publish to the Open VSX Registry via 'ovsx publish'.

Open VSX (https://open-vsx.org/) is the open-source alternative to the
VS Code Marketplace, used by VS Codium, Gitpod, Eclipse Theia, and others.
Publishing here makes the extension available to a wider audience.

Authentication requires the OVSX_PAT environment variable to be set with
a personal access token from https://open-vsx.org/.
"""

import os
from pathlib import Path

from scripts.modules.log import heading, run, success, warn


def publish(vsix_path: Path, *, cwd: Path) -> None:
    """Publish a .vsix file to the Open VSX Registry.

    This step is intentionally non-fatal.  If the OVSX_PAT token is
    missing or the upload fails, the script warns and continues — the
    primary Marketplace publish has already succeeded by this point.

    Args:
        vsix_path: Path to the .vsix file to upload.
        cwd:       Working directory for subprocess calls.
    """
    heading("Publishing to Open VSX Registry")

    ovsx_pat = os.environ.get("OVSX_PAT")
    if not ovsx_pat:
        warn(
            "OVSX_PAT environment variable is not set — skipping Open VSX.\n"
            "  To publish to Open VSX, create a token at https://open-vsx.org/\n"
            "  and set it:  export OVSX_PAT=<your-token>"
        )
        return

    result = run(
        ["ovsx", "publish", str(vsix_path), "--pat", ovsx_pat],
        cwd=cwd,
        capture=True,
        check=False,
    )

    if result.returncode != 0:
        # Not fatal — the Marketplace publish already succeeded
        warn(
            "Open VSX publish failed. Check the log for details.\n"
            "  You can retry manually:  ovsx publish <file>.vsix --pat $OVSX_PAT"
        )
    else:
        success("Published to Open VSX Registry.")
