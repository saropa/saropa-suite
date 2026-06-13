"""
Git operations for the publish pipeline — commit, push, and tag.

Before publishing, the script commits all outstanding changes and pushes
to the remote so the published version matches what's on the remote.
After a successful publish, a version tag (e.g. v1.0.1) is created and
pushed for traceability.
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


def commit_all_and_push(
    version: str, *, cwd: Path, message: str | None = None, fatal_on_error: bool = True
) -> None:
    """Stage all changes, commit with a release message, and push.

    This ensures the published version corresponds to a clean, pushed
    commit.  The commit includes everything in the working tree — not
    just package.json — so that CHANGELOG.md, README.md, and any other
    pending changes are captured in the release commit.

    Args:
        version:        Version being released, used in the default message.
        cwd:            Repository working directory.
        message:        Commit message override. Defaults to "Release v{version}".
        fatal_on_error: When True (the pre-publish commit), a commit/push
            failure aborts the run. When False (the post-publish safety
            commit), failures only warn — the publish already succeeded,
            so an unpushed straggler must not mask a live release.

    Skipped silently if the directory is not a git repository.
    """
    heading("Git commit & push")

    if not _is_git_repo(cwd=cwd):
        detail("Not a git repository — skipping commit & push.")
        return

    # Post-publish safety commits must never abort the run, so route their
    # failures through warn() instead of fatal().
    def _fail(text: str) -> None:
        if fatal_on_error:
            fatal(text)
        else:
            warn(text)

    # Check if there is anything to commit (staged + unstaged + untracked)
    result = run(
        ["git", "status", "--porcelain"],
        cwd=cwd,
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        _fail("git status failed — cannot determine working tree state.")
        return

    if not result.stdout.strip():
        detail("Working tree is clean — nothing to commit.")
    else:
        # Stage everything and commit with the given (or default) message
        run(["git", "add", "-A"], cwd=cwd)

        commit_message = message or f"Release v{version}"
        commit_result = run(
            ["git", "commit", "-m", commit_message],
            cwd=cwd,
            capture=True,
            check=False,
        )

        if commit_result.returncode != 0:
            _fail(
                f"Git commit failed.\n"
                f"  Intended message: {commit_message}\n"
                f"  Output: {commit_result.stderr.strip()}"
            )
            return
        success(f"Committed: {commit_message}")

    # Push to the remote so the published version matches the remote
    push_result = run(
        ["git", "push"],
        cwd=cwd,
        capture=True,
        check=False,
    )

    if push_result.returncode != 0:
        _fail(
            "Git push failed — cannot publish from an unpushed state.\n"
            f"  Output: {push_result.stderr.strip()}"
        )
        return
    success("Pushed to remote.")


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
        return

    success(f"Tagged: {tag_name}")

    # Push the tag to the remote
    push_result = run(
        ["git", "push", "origin", tag_name],
        cwd=cwd,
        capture=True,
        check=False,
    )
    if push_result.returncode != 0:
        warn(
            f"Failed to push tag '{tag_name}'.\n"
            f"  You can push it manually:  git push origin {tag_name}"
        )
    else:
        success(f"Pushed tag: {tag_name}")
