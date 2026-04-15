"""
Pre-flight validation checks for the Saropa Suite extension pack.

Each check function reads the project state and either succeeds silently
(with a green OK line) or calls fatal() to abort with a clear message.
Checks are ordered from cheapest/fastest to most expensive (network calls).
"""

import json
import re
from pathlib import Path

from scripts.modules.color import bold, green, red
from scripts.modules.log import (
    detail,
    fatal,
    info,
    print_and_log,
    run,
    success,
    warn,
)


# --------------------------------------------------------------------------- #
# Thresholds
# --------------------------------------------------------------------------- #

# Minimum meaningful README length (bytes).  The Marketplace renders
# README.md as the extension's landing page — a stub is not acceptable.
MIN_README_BYTES = 100

# Icon must be square, at least 128x128.  We cannot verify pixel dimensions
# without Pillow (not a dependency), so we check file size as a proxy.
MIN_ICON_BYTES = 1024  # 1 KB — any real PNG will exceed this

# Required fields that must be present and non-empty in package.json.
# Each tuple is (json_key, human_label).
REQUIRED_FIELDS = [
    ("name", "name"),
    ("displayName", "displayName"),
    ("description", "description"),
    ("version", "version"),
    ("publisher", "publisher"),
    ("license", "license"),
]


# --------------------------------------------------------------------------- #
# package.json loading
# --------------------------------------------------------------------------- #

def load_package_json(package_json: Path) -> dict:
    """Load and return the parsed package.json, or fatal on any error."""
    if not package_json.is_file():
        fatal(f"package.json not found at {package_json}")
    try:
        with open(package_json, encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        fatal(f"package.json is not valid JSON: {exc}")


# --------------------------------------------------------------------------- #
# Individual checks
# --------------------------------------------------------------------------- #

def check_required_fields(pkg: dict) -> None:
    """Verify all required top-level fields are present and non-empty."""
    missing = []
    for key, label in REQUIRED_FIELDS:
        value = pkg.get(key)
        if not value or (isinstance(value, str) and not value.strip()):
            missing.append(label)

    if missing:
        fatal(
            "package.json is missing required fields:\n"
            + "".join(f"    - {f}\n" for f in missing)
            + "  All of these are required for Marketplace publishing."
        )
    success("All required package.json fields are present.")


def check_publisher(pkg: dict) -> str:
    """Verify the publisher field and return its value."""
    publisher = pkg.get("publisher", "")
    if not publisher:
        fatal("No 'publisher' field in package.json.")
    success(f"Publisher: {publisher}")
    return publisher


def check_version(pkg: dict) -> str:
    """Verify the version is valid semver and return it."""
    version = pkg.get("version", "")
    if not version:
        fatal("No 'version' field in package.json.")
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        fatal(
            f"Version '{version}' is not valid semver (expected X.Y.Z).\n"
            "  Pre-release suffixes like -beta.1 are not supported by vsce."
        )
    info(f"Current version: {bold(version)}")
    return version


def check_engines(pkg: dict) -> None:
    """Verify the engines.vscode field is present.

    Without this, vsce will refuse to package.  The value must be a valid
    semver range (e.g. "^1.74.0").
    """
    engines = pkg.get("engines", {})
    vscode_range = engines.get("vscode", "")
    if not vscode_range:
        fatal(
            "package.json is missing engines.vscode.\n"
            "  This field is required.  Example: \"engines\": { \"vscode\": \"^1.74.0\" }"
        )
    success(f"engines.vscode: {vscode_range}")


def check_categories(pkg: dict) -> None:
    """Verify categories includes 'Extension Packs' for an extension pack."""
    categories = pkg.get("categories", [])
    if "Extension Packs" not in categories:
        warn(
            "categories does not include 'Extension Packs'.\n"
            "  This is expected for an extension pack and helps discoverability."
        )
    else:
        success("Category: Extension Packs")


def check_license(pkg: dict, root: Path) -> None:
    """Verify the license field matches a LICENSE file on disk."""
    license_id = pkg.get("license", "")
    if not license_id:
        fatal(
            "No 'license' field in package.json.\n"
            "  Set it to a valid SPDX identifier (e.g. \"MIT\")."
        )

    license_file = root / "LICENSE"
    if not license_file.is_file():
        # Also check common variants
        for variant in ["LICENSE.md", "LICENSE.txt", "LICENCE"]:
            candidate = root / variant
            if candidate.is_file():
                license_file = candidate
                break

    if not license_file.is_file():
        fatal(
            f"License is set to '{license_id}' but no LICENSE file exists.\n"
            "  Create a LICENSE file in the project root."
        )
    success(f"License: {license_id} (file: {license_file.name})")


def check_repository(pkg: dict) -> None:
    """Verify the repository field points to a URL."""
    repo = pkg.get("repository", {})
    url = repo.get("url", "") if isinstance(repo, dict) else str(repo)
    if not url:
        warn(
            "No repository.url in package.json.\n"
            "  Adding a repository URL improves trust and Marketplace SEO."
        )
    else:
        success(f"Repository: {url}")


def check_readme(readme_path: Path) -> None:
    """Verify the README exists and has meaningful content."""
    if not readme_path.is_file():
        fatal(f"README.md not found at {readme_path}")
    size = readme_path.stat().st_size
    if size < MIN_README_BYTES:
        fatal(
            f"README.md is only {size} bytes — too short for a Marketplace listing.\n"
            "  The README becomes the extension's landing page; add real content."
        )
    success(f"README.md: {size:,} bytes")


def check_icon(pkg: dict, root: Path) -> None:
    """Verify the icon file exists and is a plausible image."""
    icon_relative = pkg.get("icon")
    if not icon_relative:
        fatal("No 'icon' field in package.json.")

    icon_path = root / icon_relative
    if not icon_path.is_file():
        fatal(f"Icon file not found: {icon_path}")

    size = icon_path.stat().st_size
    if size < MIN_ICON_BYTES:
        fatal(
            f"Icon file is only {size} bytes — does not look like a real image.\n"
            f"  Path: {icon_path}"
        )

    # Verify PNG magic bytes — the Marketplace requires PNG format
    with open(icon_path, "rb") as fh:
        header = fh.read(8)
    png_magic = b"\x89PNG\r\n\x1a\n"
    if header != png_magic:
        fatal(
            f"Icon file does not appear to be a PNG.\n"
            f"  The VS Code Marketplace requires PNG format.\n"
            f"  Path: {icon_path}"
        )

    success(f"Icon: {icon_relative} ({size:,} bytes, PNG)")


def check_extension_pack_ids(pkg: dict) -> list[str]:
    """Return the list of extension IDs in the pack, or fail if empty."""
    pack_ids = pkg.get("extensionPack", [])
    if not pack_ids:
        fatal("extensionPack is empty in package.json — nothing to bundle.")

    # Validate format: each ID should be "publisher.extension-name"
    bad_ids = []
    for ext_id in pack_ids:
        if not re.match(r"^[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+$", ext_id):
            bad_ids.append(ext_id)

    if bad_ids:
        fatal(
            "Invalid extension ID format (expected 'publisher.name'):\n"
            + "".join(f"    - {eid}\n" for eid in bad_ids)
        )

    # Check for duplicates
    seen = set()
    dupes = []
    for ext_id in pack_ids:
        lower = ext_id.lower()
        if lower in seen:
            dupes.append(ext_id)
        seen.add(lower)
    if dupes:
        fatal(
            "Duplicate extension IDs in extensionPack:\n"
            + "".join(f"    - {eid}\n" for eid in dupes)
        )

    info(f"Extension pack contains {bold(str(len(pack_ids)))} extension(s):")
    for ext_id in pack_ids:
        detail(f"  - {ext_id}")
    return pack_ids


def check_vscodeignore(root: Path) -> None:
    """Warn if no .vscodeignore file exists.

    Without .vscodeignore, vsce packages everything in the directory,
    including scripts/, reports/, .git/, etc.  A .vscodeignore keeps
    the .vsix file small and avoids leaking development files.
    """
    vscodeignore = root / ".vscodeignore"
    if not vscodeignore.is_file():
        warn(
            "No .vscodeignore file found.\n"
            "  Without it, vsce packages all files (scripts, reports, .git, etc.).\n"
            "  Create a .vscodeignore to keep the .vsix clean and small."
        )
    else:
        size = vscodeignore.stat().st_size
        if size < 5:
            # An empty or near-empty file is probably a mistake
            warn(".vscodeignore exists but appears empty — review its contents.")
        else:
            success(f".vscodeignore: {size:,} bytes")


def check_marketplace_listings(pack_ids: list[str], *, cwd) -> None:
    """Verify each extension in the pack is published on the Marketplace.

    Uses 'vsce show <id>' which exits 0 if the extension exists.
    This catches typos and extensions that were never published.
    """
    missing = []
    for ext_id in pack_ids:
        result = run(
            ["vsce", "show", ext_id, "--json"],
            cwd=cwd,
            capture=True,
            check=False,
        )
        if result.returncode != 0:
            missing.append(ext_id)
            print_and_log(f"  {red('MISSING:')} {ext_id}")
        else:
            print_and_log(f"  {green('FOUND:')}   {ext_id}")

    if missing:
        fatal(
            "The following extensions are NOT published on the Marketplace:\n"
            + "".join(f"    - {eid}\n" for eid in missing)
            + "  Publish them first, or remove them from extensionPack."
        )


def check_duplicate_version(publisher: str, name: str, version: str,
                             *, cwd) -> None:
    """Warn if this exact version is already published on the Marketplace.

    Publishing the same version again will fail with a confusing error.
    This check catches that early with a clear message.
    """
    ext_id = f"{publisher}.{name}"
    result = run(
        ["vsce", "show", ext_id, "--json"],
        cwd=cwd,
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        # Extension not published yet — first publish, no conflict possible
        detail(f"{ext_id} not yet on Marketplace (first publish).")
        return

    try:
        data = json.loads(result.stdout)
        # vsce show --json returns the full extension manifest; the version
        # is nested under versions[0].version or at the top level depending
        # on the vsce version.  Try both paths.
        published_version = None
        versions = data.get("versions", [])
        if versions and isinstance(versions, list):
            published_version = versions[0].get("version")
        if not published_version:
            published_version = data.get("version")

        if published_version == version:
            warn(
                f"Version {version} of {ext_id} is already published.\n"
                "  Publishing the same version again will fail.\n"
                "  Update the version in CHANGELOG.md first (add a new ## [x.y.z] heading)."
            )
        else:
            success(
                f"Latest published version: {published_version} "
                f"(publishing {version})"
            )
    except (json.JSONDecodeError, KeyError, IndexError):
        # Could not parse — not fatal, just skip the check
        detail("Could not parse Marketplace response for version check.")


def check_node_version(*, cwd) -> None:
    """Verify Node.js is installed and log its version.

    vsce and ovsx both require Node.js.  This check catches the case
    where npm is on PATH (e.g. via nvm) but node itself is not.
    """
    result = run(["node", "--version"], cwd=cwd, capture=True, check=False)
    if result.returncode != 0:
        fatal(
            "Node.js is not installed or not on PATH.\n"
            "  vsce and ovsx require Node.js.  Install it from https://nodejs.org/"
        )
    node_version = result.stdout.strip()
    success(f"Node.js: {node_version}")


def check_git_clean(*, cwd) -> None:
    """Warn (but do not block) if the working tree has uncommitted changes.

    Publishing from a dirty tree is not an error, but it means the
    published version won't correspond to a clean commit.
    """
    # Check if this is a git repo at all
    result = run(["git", "rev-parse", "--is-inside-work-tree"],
                 cwd=cwd, capture=True, check=False)
    if result.returncode != 0:
        detail("Not a git repository — skipping dirty-tree check.")
        return

    result = run(["git", "status", "--porcelain"],
                 cwd=cwd, capture=True, check=False)
    if result.returncode == 0 and result.stdout.strip():
        warn("Working tree has uncommitted changes.")
        detail("Consider committing before publishing so the version tag is clean.")
    else:
        success("Git working tree is clean.")


def check_git_tag_conflict(version: str, *, cwd) -> None:
    """Warn if a git tag for this version already exists.

    If the tag v1.0.0 already exists, the user probably forgot to
    bump the version.  This is a warning, not a fatal error.
    """
    # Check if this is a git repo at all
    result = run(["git", "rev-parse", "--is-inside-work-tree"],
                 cwd=cwd, capture=True, check=False)
    if result.returncode != 0:
        return  # Not a git repo — nothing to check

    tag_name = f"v{version}"
    result = run(
        ["git", "tag", "--list", tag_name],
        cwd=cwd, capture=True, check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        warn(
            f"Git tag '{tag_name}' already exists.\n"
            "  This usually means the version was already published.\n"
            "  Update the version in CHANGELOG.md (add a new ## [x.y.z] heading)."
        )
    else:
        success(f"Git tag '{tag_name}' is available.")
