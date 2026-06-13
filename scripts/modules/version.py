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


def _bump(version: str, level: str) -> str:
    """Return *version* incremented at the given semver *level*.

    level is one of "major", "minor", "patch". A higher-level bump zeroes
    the lower components (1.2.3 --minor--> 1.3.0) per semver.
    """
    major, minor, patch = (int(part) for part in version.split("."))
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def promote_unreleased(changelog_path: Path, bump: str = "patch") -> str | None:
    """Promote a non-empty ``## [Unreleased]`` section to a new version.

    The Marketplace rejects re-uploading an existing version, so changes
    accumulated under ``## [Unreleased]`` must become a fresh numbered
    release before publishing. This:

      1. Confirms an ``## [Unreleased]`` heading exists and has at least
         one bullet entry under it (an empty section is nothing to ship).
      2. Computes the next version by bumping the latest released version
         (the first ``## [x.y.z]`` heading) at *bump* level.
      3. Renames the Unreleased heading to ``## [x.y.z]`` in place.

    No empty ``## [Unreleased]`` placeholder is left behind — an empty
    heading sitting directly above the new version is noise. The next
    release's changes get a fresh ``## [Unreleased]`` heading when they
    are written.

    Returns the new version string, or None when there is nothing to
    promote (no Unreleased heading, or it has no entries) — in which case
    the caller falls back to the existing latest version.
    """
    content = changelog_path.read_text(encoding="utf-8")

    # Locate the Unreleased heading. Case-insensitive so "[unreleased]"
    # written by hand still matches.
    heading_match = re.search(
        r"^##\s+\[Unreleased\].*$", content, re.MULTILINE | re.IGNORECASE
    )
    if heading_match is None:
        return None

    # The section body runs from the end of the heading line to the next
    # "## " heading (or end of file). A release needs real entries — a
    # body with no "- " bullet is empty and must not trigger a bump.
    body_start = heading_match.end()
    next_heading = re.search(r"^##\s+", content[body_start:], re.MULTILINE)
    body = (
        content[body_start : body_start + next_heading.start()]
        if next_heading
        else content[body_start:]
    )
    if re.search(r"^\s*-\s+\S", body, re.MULTILINE) is None:
        return None  # Unreleased section is empty — nothing to release

    latest = read_changelog_version(changelog_path)
    new_version = _bump(latest, bump)

    # Rename the Unreleased heading to the new version in place. No empty
    # placeholder is seeded — the next release writes its own heading.
    replacement = f"## [{new_version}]"
    content = content[: heading_match.start()] + replacement + content[heading_match.end():]
    changelog_path.write_text(content, encoding="utf-8")

    success(
        f"Promoted CHANGELOG [Unreleased] -> [{new_version}] "
        f"({bump} bump from {latest})"
    )
    return new_version


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
