"""
Publish to the VS Code Marketplace via 'vsce publish'.
"""

from pathlib import Path

from scripts.modules.log import fatal, heading, run, success


def publish(root: Path) -> None:
    """Run 'vsce publish' to push the extension to the VS Code Marketplace.

    Assumes the extension has already been packaged and that vsce is
    authenticated (via 'vsce login' or a VSCE_PAT environment variable).

    Captures output and gives a clear error message on failure instead
    of letting the subprocess exception propagate with a raw traceback.
    """
    heading("Publishing to VS Code Marketplace")
    result = run(["vsce", "publish"], cwd=root, capture=True, check=False)

    if result.returncode != 0:
        # Pull the most useful line from vsce's stderr/stdout for the
        # error message.  vsce prints "ERROR" lines to stderr.
        output = (result.stderr or "") + (result.stdout or "")
        detail = ""
        for line in output.splitlines():
            stripped = line.strip()
            if stripped:
                # Use the first non-empty line as the detail
                detail = stripped
                break

        fatal(
            f"vsce publish failed (exit code {result.returncode}).\n"
            + (f"  vsce says: {detail}\n" if detail else "")
            + "  Check the log file for full output."
        )

    success("Published to VS Code Marketplace.")
