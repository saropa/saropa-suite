"""
Publish to the VS Code Marketplace via 'vsce publish'.
"""

# cspell:ignore itemname

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
        # Pull the most useful lines from vsce's stderr/stdout.
        # vsce prints "ERROR" lines to stderr.
        output = (result.stderr or "") + (result.stdout or "")
        lines = [ln.strip() for ln in output.splitlines() if ln.strip()]

        # Identify whether this is a PAT / auth problem so the error
        # message can include targeted remediation steps.
        is_auth_error = any(
            keyword in output
            for keyword in (
                "Personal Access Token",
                "not authorized",
                "TF400813",
                "401",
                "credential",
            )
        )

        detail = lines[0] if lines else ""
        auth_hint = ""
        if is_auth_error:
            auth_hint = (
                "\n\n  This looks like a PAT / authentication problem.\n"
                "  Re-run the publish script — it validates the PAT\n"
                "  before attempting to publish and will give detailed\n"
                "  remediation steps if the token is bad."
            )

        fatal(
            f"vsce publish failed (exit code {result.returncode}).\n"
            + (f"  vsce says: {detail}\n" if detail else "")
            + "  Check the log file for full output."
            + auth_hint
        )

    success("Published to VS Code Marketplace.")
