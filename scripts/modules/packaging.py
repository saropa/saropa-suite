"""
Extension packaging — runs 'vsce package' and locates the output .vsix.
"""

import os
from pathlib import Path

from scripts.modules.log import fatal, heading, run, success


def package_extension(root: Path) -> Path:
    """Run 'vsce package' and return the path to the generated .vsix file.

    The .vsix is created in the project root by vsce.  After packaging,
    this function locates the most recently modified .vsix to handle
    cases where old .vsix files exist from previous runs.
    """
    heading("Packaging extension")
    run(["vsce", "package"], cwd=root)

    # Find the .vsix file that was just created (most recent by mtime)
    vsix_files = sorted(root.glob("*.vsix"), key=os.path.getmtime, reverse=True)
    if not vsix_files:
        fatal("vsce package succeeded but no .vsix file was found.")

    vsix_path = vsix_files[0]
    size = vsix_path.stat().st_size
    success(f"Package created: {vsix_path.name} ({size:,} bytes)")
    return vsix_path
