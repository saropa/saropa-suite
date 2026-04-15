"""
npm global tool management — auto-install and auto-update.

Ensures that CLI tools like vsce and ovsx are installed and running
the latest version before the publish pipeline begins.  This prevents
the "you have an outdated version" warning from appearing mid-publish.
"""

import json
import shutil

from scripts.modules.log import fatal, info, run, success, warn


def _get_installed_version(package_name: str, *, cwd) -> str | None:
    """Return the installed version of a global npm package, or None."""
    result = run(
        ["npm", "list", "-g", package_name, "--json"],
        cwd=cwd,
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
        # npm list --json nests under "dependencies"
        deps = data.get("dependencies", {})
        pkg_info = deps.get(package_name, {})
        return pkg_info.get("version")
    except (json.JSONDecodeError, KeyError):
        return None


def _get_latest_version(package_name: str, *, cwd) -> str | None:
    """Query the npm registry for the latest version of a package."""
    result = run(
        ["npm", "view", package_name, "version"],
        cwd=cwd,
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def install_or_update(package_name: str, display_name: str, *, cwd) -> None:
    """
    Ensure a global npm tool is installed and up-to-date.

    - If the tool is not installed, it is installed automatically.
    - If the tool is outdated, it is updated to the latest version.
    - If the npm registry is unreachable, the script proceeds with
      whatever version is already installed (with a warning).
    """
    installed = _get_installed_version(package_name, cwd=cwd)

    if installed is None:
        # Not installed at all — install it
        info(f"{display_name} is not installed. Installing...")
        result = run(
            ["npm", "install", "-g", package_name],
            cwd=cwd,
            capture=True,
            check=False,
        )
        if result.returncode != 0:
            fatal(
                f"Failed to install {package_name}.\n"
                f"  Try manually:  npm install -g {package_name}"
            )
        installed = _get_installed_version(package_name, cwd=cwd)
        success(f"Installed {display_name} v{installed}")
        return

    # Already installed — check if there is a newer version available
    latest = _get_latest_version(package_name, cwd=cwd)

    if latest is None:
        # Could not reach the registry — proceed with what we have
        warn(f"Could not check for {display_name} updates (registry unreachable).")
        info(f"Proceeding with installed {display_name} v{installed}")
        return

    if installed == latest:
        success(f"{display_name} v{installed} (latest)")
        return

    # Outdated — update automatically
    info(
        f"{display_name} v{installed} is outdated "
        f"(latest is v{latest}). Updating..."
    )
    result = run(
        ["npm", "install", "-g", package_name],
        cwd=cwd,
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        # Update failed — not fatal, proceed with the old version
        warn(
            f"Failed to update {display_name}. "
            f"Continuing with v{installed}."
        )
    else:
        updated = _get_installed_version(package_name, cwd=cwd) or latest
        success(f"Updated {display_name} to v{updated}")


def ensure_vsce(*, cwd) -> None:
    """Ensure vsce (@vscode/vsce) is installed, up-to-date, and on PATH."""
    install_or_update("@vscode/vsce", "vsce", cwd=cwd)
    if shutil.which("vsce") is None:
        fatal(
            "vsce was installed but is not on PATH.\n"
            "  You may need to restart your terminal or fix your npm prefix."
        )


def ensure_ovsx(*, cwd) -> None:
    """Ensure ovsx is installed, up-to-date, and on PATH."""
    install_or_update("ovsx", "ovsx", cwd=cwd)
    if shutil.which("ovsx") is None:
        fatal(
            "ovsx was installed but is not on PATH.\n"
            "  You may need to restart your terminal or fix your npm prefix."
        )
