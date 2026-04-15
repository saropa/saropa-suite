"""
Git operations for the publish pipeline — commit and tag.

After a version bump, the script commits the changed package.json so the
published version corresponds to a clean commit.  After a successful
publish, a version tag (e.g. v1.0.1) is created for traceability.
"""

from pathlib import Path

from scripts.modules.log import detail, fatal, heading, run, success, warn


def _is_git_repo(*, cwd: Path) -> bool:
    """Return True if cwd is inside a git working tree."""
    result = run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=cwd,
        capture=True,
        check=False,
    )
    return result.returncode == 0


def commit_version_bump(version: str, *, cwd: Path) -> None:
    """Stage package.json and commit the version bump.

    Skipped silently if:
    - The directory is not a git repository.
    - package.json has no staged or unstaged changes (nothing to commit).

    The commit message follows the conventional format:
        chore: bump version to X.Y.Z
    """
    heading("Git commit")

    if not _is_git_repo(cwd=cwd):
        detail("Not a git repository — skipping commit.")
        return

    # Check if package.json actually has changes to commit
    result = run(
        ["git", "diff", "--name-only", "package.json"],
        cwd=cwd,
        capture=True,
        check=False,
    )
    has_unstaged = result.returncode == 0 and result.stdout.strip()

    result = run(
        ["git", "diff", "--cached", "--name-only", "package.json"],
        cwd=cwd,
        capture=True,
        check=False,
    )
    has_staged = result.returncode == 0 and result.stdout.strip()

    if not has_unstaged and not has_staged:
        detail("package.json has no changes — skipping commit.")
        return

    # Stage package.json (only this file — don't sweep in unrelated changes)
    run(["git", "add", "package.json"], cwd=cwd)

    # Commit with a conventional message
    message = f"chore: bump version to {version}"
    result = run(
        ["git", "commit", "-m", message],
        cwd=cwd,
        capture=True,
        check=False,
    )

    if result.returncode != 0:
        # Commit failed — warn but don't abort the publish pipeline.
        # The user can commit manually afterward.
        warn(
            f"Git commit failed. You may need to commit manually.\n"
            f"  Intended message: {message}"
        )
    else:
        success(f"Committed: {message}")


def tag_version(version: str, *, cwd: Path) -> None:
    """Create an annotated git tag for the published version.

    The tag format is vX.Y.Z (e.g. v1.0.1).  If the tag already exists,
    a warning is printed and the step is skipped — the publish has already
    succeeded at this point, so this is not fatal.

    Skipped silently if the directory is not a git repository.
    """
    heading("Git tag")

    if not _is_git_repo(cwd=cwd):
        detail("Not a git repository — skipping tag.")
        return

    tag_name = f"v{version}"

    # Check if the tag already exists (shouldn't at this point, but be safe)
    result = run(
        ["git", "tag", "--list", tag_name],
        cwd=cwd,
        capture=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        warn(f"Tag '{tag_name}' already exists — skipping.")
        return

    # Create an annotated tag with a descriptive message
    result = run(
        ["git", "tag", "-a", tag_name, "-m", f"Release {version}"],
        cwd=cwd,
        capture=True,
        check=False,
    )

    if result.returncode != 0:
        warn(
            f"Failed to create tag '{tag_name}'.\n"
            f"  You can create it manually:  git tag -a {tag_name} -m \"Release {version}\""
        )
    else:
        success(f"Tagged: {tag_name}")
        detail(f"Push with:  git push origin {tag_name}")
