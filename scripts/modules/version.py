"""
Version management for package.json using CHANGELOG.md as the source of truth.

The latest ## [x.y.z] heading in CHANGELOG.md determines the version.
If package.json disagrees, it is updated to match.  Only the "version"
field is touched — the rest of package.json is preserved byte-for-byte
to avoid reformatting.
"""

import re
from pathlib import Path

from scripts.modules.log import fatal, info, success

from scripts.modules.color import bold, yellow


def read_changelog_version(changelog_path: Path) -> str:
    """Parse the latest version from CHANGELOG.md.

    Looks for the first heading matching ``## [x.y.z]`` and returns the
    version string.  Fatals if no valid version heading is found or if
    the version is not valid semver.

    Args:
        changelog_path: Absolute path to CHANGELOG.md.

    Returns:
        The version string from the first version heading, e.g. "1.0.1".
    """
    if not changelog_path.is_file():
        fatal(f"CHANGELOG.md not found at {changelog_path}")

    with open(changelog_path, encoding="utf-8") as fh:
        for line in fh:
            # Match lines like "## [1.0.1]" or "## [1.0.1] - 2026-04-14"
            match = re.match(r"^##\s+\[(\d+\.\d+\.\d+)\]", line)
            if match:
                version = match.group(1)
                # Validate it's proper semver (X.Y.Z, no extras)
                if not re.match(r"^\d+\.\d+\.\d+$", version):
                    fatal(
                        f"CHANGELOG.md version '{version}' is not valid "
                        "semver (expected X.Y.Z)."
                    )
                return version

    fatal(
        "No version heading found in CHANGELOG.md.\n"
        "  Expected a heading like: ## [1.0.1]\n"
        "  The first ## [x.y.z] heading is used as the publish version."
    )


def sync_version_from_changelog(
    package_json: Path, changelog_path: Path, pkg_version: str
) -> str:
    """Compare CHANGELOG.md version to package.json and sync if needed.

    If the versions match, this is a no-op.  If they differ, package.json
    is updated to match the changelog version.

    Args:
        package_json:   Path to package.json.
        changelog_path: Path to CHANGELOG.md.
        pkg_version:    Current version string from package.json.

    Returns:
        The version that will be published (always the changelog version).
    """
    changelog_version = read_changelog_version(changelog_path)

    if changelog_version == pkg_version:
        success(
            f"CHANGELOG.md and package.json versions match: {changelog_version}"
        )
        return changelog_version

    # Versions differ — update package.json to match the changelog
    info(
        f"Version sync: package.json has {bold(pkg_version)}, "
        f"CHANGELOG.md has {bold(changelog_version)}"
    )
    info(
        f"Updating package.json: {pkg_version} {yellow('->')} "
        f"{bold(changelog_version)}"
    )
    write_version(package_json, changelog_version)
    return changelog_version


def write_version(package_json: Path, new_version: str) -> None:
    """Update the version field in package.json on disk.

    Uses a targeted regex replacement so only the "version" value changes.
    The rest of the file (formatting, field order, comments) is untouched.
    """
    with open(package_json, encoding="utf-8") as fh:
        content = fh.read()

    updated, count = re.subn(
        r'("version"\s*:\s*)"[^"]+"',
        rf'\1"{new_version}"',
        content,
        count=1,
    )

    if count != 1:
        fatal("Failed to update version in package.json — regex did not match.")

    with open(package_json, "w", encoding="utf-8") as fh:
        fh.write(updated)

    success(f"Updated package.json version to {new_version}")
