#!/usr/bin/env python3
"""
Publish script for the Saropa Suite VS Code extension pack.

Validates all prerequisites, packages the extension, and publishes
to the VS Code Marketplace and (optionally) Open VSX Registry.
All output is colored in the terminal and a full plain-text log is
written to reports/<yyyymmdd>/<datetime>_publish.log.

This is the entry point.  All logic lives in scripts/modules/:
    color.py               — ANSI terminal colors
    log.py                 — dual terminal + log-file output, subprocess runner
    npm_tools.py           — auto-install/update of vsce and ovsx
    checks.py              — pre-flight validation (package.json, icon, etc.)
    version.py             — version sync from CHANGELOG.md
    git.py                 — commit, push, and tag releases
    packaging.py           — vsce package
    publish_marketplace.py — vsce publish
    publish_openvsx.py     — ovsx publish

Usage:
    python scripts/publish.py              # full publish (Marketplace + Open VSX)
    python scripts/publish.py --dry-run    # validate + package only, no publish
    python scripts/publish.py --skip-ovsx  # skip Open VSX, Marketplace only

Version is determined by the first ## [x.y.z] heading in CHANGELOG.md.
If package.json has a different version, it is updated automatically.
"""

# cspell:disable

import argparse
import sys
from pathlib import Path

# Ensure the project root is on sys.path so "scripts.modules.*" imports
# resolve regardless of where the script is invoked from.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.modules.checks import (
    check_categories,
    check_duplicate_version,
    check_engines,
    check_extension_pack_ids,
    check_git_tag_conflict,
    check_icon,
    check_license,
    check_marketplace_listings,
    check_node_version,
    check_publisher,
    check_readme,
    check_repository,
    check_required_fields,
    check_version,
    check_vscodeignore,
    load_package_json,
)
from scripts.modules.color import bold, dim
from scripts.modules.git import commit_all_and_push, tag_version
from scripts.modules.log import (
    close_log_file,
    confirm,
    heading,
    info,
    init_log_file,
    success,
)
from scripts.modules.npm_tools import ensure_ovsx, ensure_vsce
from scripts.modules.packaging import package_extension
from scripts.modules.publish_marketplace import publish as publish_to_marketplace
from scripts.modules.publish_openvsx import publish as publish_to_openvsx
from scripts.modules.version import sync_version_from_changelog


# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

PACKAGE_JSON = ROOT / "package.json"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
README_PATH = ROOT / "README.md"
REPORTS_DIR = ROOT / "reports"


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
    parser.add_argument(
        "--skip-ovsx",
        action="store_true",
        help="Skip publishing to Open VSX Registry (Marketplace only).",
    )
    args = parser.parse_args()

    # ---- Initialize log file ---------------------------------------------- #
    log_path = init_log_file(REPORTS_DIR)
    info(f"Log file: {dim(str(log_path))}")

    try:
        # ---- Tool setup --------------------------------------------------- #
        # Install or update vsce (and ovsx if needed) before anything else,
        # so we never hit "outdated vsce" warnings mid-publish.
        heading("Tool setup")
        check_node_version(cwd=ROOT)
        ensure_vsce(cwd=ROOT)
        if not args.skip_ovsx and not args.dry_run:
            ensure_ovsx(cwd=ROOT)

        # ---- Pre-flight checks -------------------------------------------- #
        heading("Pre-flight checks")

        pkg = load_package_json(PACKAGE_JSON)
        check_required_fields(pkg)
        publisher = check_publisher(pkg)
        current_version = check_version(pkg)
        check_engines(pkg)
        check_categories(pkg)
        check_license(pkg, ROOT)
        check_repository(pkg)
        check_readme(README_PATH)
        check_icon(pkg, ROOT)
        check_vscodeignore(ROOT)
        pack_ids = check_extension_pack_ids(pkg)

        # ---- Network checks (slower) ------------------------------------- #
        heading("Verifying pack extensions exist on Marketplace")
        check_marketplace_listings(pack_ids, cwd=ROOT)

        # ---- Sync version from CHANGELOG.md --------------------------------- #
        # CHANGELOG.md is the source of truth for the version.  If
        # package.json disagrees, it is updated to match automatically.
        heading("Version sync (CHANGELOG.md → package.json)")
        current_version = sync_version_from_changelog(
            PACKAGE_JSON, CHANGELOG_PATH, current_version
        )

        # ---- Commit & push ------------------------------------------------ #
        # Commit all outstanding changes (version sync, CHANGELOG, README,
        # etc.) and push so the published version matches the remote.
        commit_all_and_push(current_version, cwd=ROOT)

        heading("Version and git checks")
        name = pkg.get("name", "saropa-suite")
        check_duplicate_version(publisher, name, current_version, cwd=ROOT)
        check_git_tag_conflict(current_version, cwd=ROOT)

        # ---- Package ------------------------------------------------------ #
        vsix_path = package_extension(ROOT)

        # ---- Publish (unless dry-run) ------------------------------------- #
        if args.dry_run:
            heading("Dry run complete")
            info(f"Package ready at: {bold(str(vsix_path))}")
            info("Skipping publish (--dry-run).")
            info(f"Full log: {dim(str(log_path))}")
            return

        heading("Ready to publish")
        info(f"Publisher:  {bold(publisher)}")
        info(f"Version:    {bold(current_version)}")
        info(f"Package:    {bold(vsix_path.name)}")
        info(f"Extensions: {', '.join(pack_ids)}")

        targets = "VS Code Marketplace"
        if not args.skip_ovsx:
            targets += " + Open VSX"
        info(f"Targets:    {bold(targets)}")

        if not confirm(f"Publish to {targets}?"):
            info(
                "Aborted. The .vsix file is still available for manual publishing."
            )
            return

        # Publish to VS Code Marketplace first (primary target)
        publish_to_marketplace(ROOT)

        # Publish to Open VSX (secondary, non-fatal if it fails)
        if not args.skip_ovsx:
            publish_to_openvsx(vsix_path, cwd=ROOT)

        # Tag the commit after successful publish so the tag points to
        # the exact commit that was published.
        tag_version(current_version, cwd=ROOT)

        # ---- Summary ----------------------------------------------------- #
        heading("Done")
        success(f"Saropa Suite v{current_version} is live.")
        info(
            f"  Marketplace: https://marketplace.visualstudio.com/items?"
            f"itemName={publisher}.saropa-suite"
        )
        if not args.skip_ovsx:
            info(
                f"  Open VSX:    https://open-vsx.org/extension/"
                f"{publisher}/saropa-suite"
            )
        info(f"Full log: {dim(str(log_path))}")

    finally:
        close_log_file()


if __name__ == "__main__":
    main()
