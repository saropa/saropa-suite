#!/usr/bin/env python3
"""
Publish script for the Saropa Suite VS Code extension pack.

Validates all prerequisites, packages the extension, and publishes
to the VS Code Marketplace.

Usage:
    python scripts/publish.py              # full publish
    python scripts/publish.py --dry-run    # validate + package only, no publish
    python scripts/publish.py --patch      # bump patch version, then publish
    python scripts/publish.py --minor      # bump minor version, then publish
    python scripts/publish.py --major      # bump major version, then publish
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

# Root of the extension pack (one level up from scripts/)
ROOT = Path(__file__).resolve().parent.parent

PACKAGE_JSON = ROOT / "package.json"
README_PATH = ROOT / "README.md"

# Minimum meaningful README length (bytes).  The Marketplace renders
# README.md as the extension's landing page — a stub is not acceptable.
MIN_README_BYTES = 100

# Icon must be square, at least 128x128.  We cannot verify dimensions
# without Pillow, so we just verify the file exists and is non-empty.
MIN_ICON_BYTES = 1024  # 1 KB — any real PNG will exceed this


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def fatal(message: str) -> None:
    """Print an error message and exit with a non-zero status."""
    print(f"\n  ERROR: {message}\n", file=sys.stderr)
    sys.exit(1)


def info(message: str) -> None:
    print(f"  {message}")


def heading(message: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {message}")
    print(f"{'=' * 60}")


def run(cmd: list[str], *, cwd: Path = ROOT, check: bool = True,
        capture: bool = False) -> subprocess.CompletedProcess:
    """Run a subprocess, echoing the command first."""
    display_cmd = " ".join(cmd)
    info(f"$ {display_cmd}")
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        text=True,
        capture_output=capture,
    )


def confirm(prompt: str) -> bool:
    """Ask the user a yes/no question.  Returns True on 'y'."""
    answer = input(f"\n  {prompt} [y/N] ").strip().lower()
    return answer == "y"


# --------------------------------------------------------------------------- #
# Validation steps
# --------------------------------------------------------------------------- #

def load_package_json() -> dict:
    """Load and return the parsed package.json."""
    if not PACKAGE_JSON.is_file():
        fatal(f"package.json not found at {PACKAGE_JSON}")
    with open(PACKAGE_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def check_vsce_installed() -> str:
    """Verify vsce is available and return its path."""
    vsce_path = shutil.which("vsce")
    if vsce_path is None:
        fatal(
            "vsce is not installed or not on PATH.\n"
            "  Install it with:  npm install -g @vscode/vsce"
        )
    # Print version for the log
    result = run(["vsce", "--version"], capture=True, check=False)
    if result.returncode == 0:
        info(f"vsce version: {result.stdout.strip()}")
    return vsce_path


def check_publisher(pkg: dict) -> str:
    """Verify the publisher field is present and return it."""
    publisher = pkg.get("publisher")
    if not publisher:
        fatal("No 'publisher' field in package.json.")
    info(f"Publisher: {publisher}")
    return publisher


def check_version(pkg: dict) -> str:
    """Return the current version string."""
    version = pkg.get("version")
    if not version:
        fatal("No 'version' field in package.json.")
    info(f"Current version: {version}")
    return version


def check_readme() -> None:
    """Verify the README exists and has meaningful content."""
    if not README_PATH.is_file():
        fatal(f"README.md not found at {README_PATH}")
    size = README_PATH.stat().st_size
    if size < MIN_README_BYTES:
        fatal(
            f"README.md is only {size} bytes — too short for a Marketplace listing.\n"
            "  The README becomes the extension's landing page; add real content."
        )
    info(f"README.md: {size:,} bytes — OK")


def check_icon(pkg: dict) -> None:
    """Verify the icon file exists and is a plausible image."""
    icon_relative = pkg.get("icon")
    if not icon_relative:
        fatal("No 'icon' field in package.json.")

    icon_path = ROOT / icon_relative
    if not icon_path.is_file():
        fatal(f"Icon file not found: {icon_path}")

    size = icon_path.stat().st_size
    if size < MIN_ICON_BYTES:
        fatal(
            f"Icon file is only {size} bytes — does not look like a real image.\n"
            f"  Path: {icon_path}"
        )
    info(f"Icon: {icon_relative} ({size:,} bytes) — OK")


def check_extension_pack_ids(pkg: dict) -> list[str]:
    """Return the list of extension IDs in the pack, or fail if empty."""
    pack_ids = pkg.get("extensionPack", [])
    if not pack_ids:
        fatal("extensionPack is empty in package.json — nothing to bundle.")
    info(f"Extension pack contains {len(pack_ids)} extension(s):")
    for ext_id in pack_ids:
        info(f"  - {ext_id}")
    return pack_ids


def check_marketplace_listings(pack_ids: list[str]) -> None:
    """
    Verify each extension in the pack is actually published on the
    Marketplace.  Uses 'vsce show <id>' which exits 0 if the extension
    exists.  This catches typos and extensions that were never published.
    """
    missing = []
    for ext_id in pack_ids:
        result = run(
            ["vsce", "show", ext_id, "--json"],
            capture=True,
            check=False,
        )
        if result.returncode != 0:
            missing.append(ext_id)
            info(f"  MISSING on Marketplace: {ext_id}")
        else:
            info(f"  Found on Marketplace:   {ext_id}")

    if missing:
        fatal(
            "The following extensions are NOT published on the Marketplace:\n"
            + "".join(f"    - {eid}\n" for eid in missing)
            + "  Publish them first, or remove them from extensionPack."
        )


def check_git_clean() -> None:
    """
    Warn (but do not block) if the working tree has uncommitted changes.
    Publishing from a dirty tree is not an error, but is worth flagging.
    """
    # Check if this is a git repo at all
    result = run(["git", "rev-parse", "--is-inside-work-tree"],
                 capture=True, check=False)
    if result.returncode != 0:
        info("Not a git repository — skipping dirty-tree check.")
        return

    result = run(["git", "status", "--porcelain"], capture=True, check=False)
    if result.returncode == 0 and result.stdout.strip():
        info("WARNING: Working tree has uncommitted changes.")
        info("Consider committing before publishing so the version tag is clean.")


# --------------------------------------------------------------------------- #
# Version bumping
# --------------------------------------------------------------------------- #

def bump_version(current: str, bump: str) -> str:
    """
    Bump a semver version string.  Returns the new version.
    bump is one of 'patch', 'minor', 'major'.
    """
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", current)
    if not match:
        fatal(f"Version '{current}' is not valid semver (expected X.Y.Z).")

    major, minor, patch = (int(g) for g in match.groups())

    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    elif bump == "patch":
        patch += 1
    else:
        fatal(f"Unknown bump type: {bump}")

    return f"{major}.{minor}.{patch}"


def write_version(new_version: str) -> None:
    """Update the version field in package.json."""
    with open(PACKAGE_JSON, encoding="utf-8") as fh:
        content = fh.read()

    # Replace only the "version" value to avoid reformatting the whole file.
    # This regex matches the "version": "X.Y.Z" line specifically.
    updated, count = re.subn(
        r'("version"\s*:\s*)"[^"]+"',
        rf'\1"{new_version}"',
        content,
        count=1,
    )

    if count != 1:
        fatal("Failed to update version in package.json — regex did not match.")

    with open(PACKAGE_JSON, "w", encoding="utf-8") as fh:
        fh.write(updated)

    info(f"Updated package.json version to {new_version}")


# --------------------------------------------------------------------------- #
# Package & Publish
# --------------------------------------------------------------------------- #

def package_extension() -> Path:
    """
    Run 'vsce package' and return the path to the generated .vsix file.
    """
    heading("Packaging extension")
    run(["vsce", "package"])

    # Find the .vsix file that was just created
    vsix_files = sorted(ROOT.glob("*.vsix"), key=os.path.getmtime, reverse=True)
    if not vsix_files:
        fatal("vsce package succeeded but no .vsix file was found.")

    vsix_path = vsix_files[0]
    size = vsix_path.stat().st_size
    info(f"Package created: {vsix_path.name} ({size:,} bytes)")
    return vsix_path


def publish_extension() -> None:
    """Run 'vsce publish' to push to the Marketplace."""
    heading("Publishing to VS Code Marketplace")
    run(["vsce", "publish"])
    info("Published successfully.")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate, package, and publish the Saropa Suite extension pack."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run all checks and package the .vsix, but do NOT publish.",
    )
    bump_group = parser.add_mutually_exclusive_group()
    bump_group.add_argument("--patch", action="store_true",
                            help="Bump the patch version before publishing.")
    bump_group.add_argument("--minor", action="store_true",
                            help="Bump the minor version before publishing.")
    bump_group.add_argument("--major", action="store_true",
                            help="Bump the major version before publishing.")
    args = parser.parse_args()

    # ---- Pre-flight checks ------------------------------------------------ #
    heading("Pre-flight checks")

    pkg = load_package_json()
    check_vsce_installed()
    publisher = check_publisher(pkg)
    current_version = check_version(pkg)
    check_readme()
    check_icon(pkg)
    pack_ids = check_extension_pack_ids(pkg)

    heading("Verifying pack extensions exist on Marketplace")
    check_marketplace_listings(pack_ids)

    check_git_clean()

    # ---- Version bump (if requested) -------------------------------------- #
    if args.patch or args.minor or args.major:
        bump_type = "patch" if args.patch else ("minor" if args.minor else "major")
        heading(f"Bumping {bump_type} version")
        new_version = bump_version(current_version, bump_type)
        info(f"Version: {current_version} -> {new_version}")
        if not confirm(f"Bump version to {new_version}?"):
            fatal("Aborted by user.")
        write_version(new_version)
        # Reload so the rest of the script sees the new version
        current_version = new_version

    # ---- Package ---------------------------------------------------------- #
    vsix_path = package_extension()

    # ---- Publish (unless dry-run) ----------------------------------------- #
    if args.dry_run:
        heading("Dry run complete")
        info(f"Package ready at: {vsix_path}")
        info("Skipping publish (--dry-run).")
        return

    heading("Ready to publish")
    info(f"Publisher:  {publisher}")
    info(f"Version:    {current_version}")
    info(f"Package:    {vsix_path.name}")
    info(f"Extensions: {', '.join(pack_ids)}")

    if not confirm("Publish to the VS Code Marketplace?"):
        info("Aborted. The .vsix file is still available for manual publishing.")
        return

    publish_extension()

    heading("Done")
    info(f"Saropa Suite v{current_version} is live on the Marketplace.")
    info(
        f"View at: https://marketplace.visualstudio.com/items?itemName={publisher}.saropa-suite"
    )


if __name__ == "__main__":
    main()
