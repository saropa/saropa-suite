# Changelog

All notable changes to the **Saropa Suite** extension pack will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- cspell:disable -->

## [1.0.8]

### Added

- **Saropa Workspace added to the suite** — `saropa.saropa-workspace` is now bundled in `extensionPack`, making the suite a four-extension install. Saropa Workspace is a project-aware launcher: pin any file or script as a favorite (single-click opens, double-click runs), with project/global scopes, scheduling, auto-detected recipes, groups, and run-target inference. The README "What's Included" section, "Better Together" integrations, suite description, keywords, and architecture diagram were updated to include it, and its icon was added to `images/` (`package.json`, `README.md`, `images/icon_saropa_workspace.png`).

## [1.0.7]

### Changed

- **Version promotion no longer leaves an empty `[Unreleased]` placeholder** — when promoting `## [Unreleased]` to a numbered release, the publish script now renames the heading in place instead of seeding a fresh empty `## [Unreleased]` above the new version. An empty heading directly above the latest release was noise; the next release's changes get a new `## [Unreleased]` heading when they are written (`scripts/modules/version.py`).

## [1.0.6]

### Added

- **Automatic version bump from `[Unreleased]`** — the publish script now promotes a non-empty `## [Unreleased]` section to a new numbered release before packaging: it bumps the latest version (patch by default, override with `--bump major|minor|patch`), renames the heading to the new version, and seeds a fresh empty `## [Unreleased]`. This prevents the "version already exists and cannot be modified" Marketplace rejection that occurred when changes accumulated under `[Unreleased]` while the version parser kept reusing the last numbered heading (`scripts/modules/version.py`, `scripts/publish.py`).
- **Final safety commit after publish** — once the version is live, the script commits and pushes any remaining working-tree changes (e.g. edits made during browser upload) so no released code is left unsaved. This post-publish commit is non-fatal: since the release already succeeded, a commit/push straggler only warns instead of aborting (`scripts/modules/git.py`, `scripts/publish.py`).

### Fixed

- **Publish script no longer aborts when npm's global bin is off PATH** — `ensure_vsce`/`ensure_ovsx` previously failed with "vsce was installed but is not on PATH" whenever the npm global prefix (e.g. `C:\Users\<user>\AppData\Roaming\npm`) was missing from the shell PATH, even though the install succeeded. They now resolve the prefix via `npm config get prefix` and prepend the global bin directory to the process PATH before the reachability check, so every `vsce`/`ovsx` subprocess works regardless of shell PATH state (`scripts/modules/npm_tools.py`).

### Changed

- **README feature list** — added Log Capture's Crashlytics & Vitals panel (Firebase crash issues, crash-free users/sessions, trend sparklines, issue archiving, background alerts) and the interactive Session Flow Map to the Log Capture section, and clarified Drift Advisor's security posture as secure-by-default (loopback-only binding, no wildcard CORS).

## [1.0.5]

### Changed

- **Reorganized image assets** — moved screenshots from `assets/screenshots/` to `images/screenshots/` and removed the `assets/` folder. All images now live under a single `images/` directory.
- **Extension icons in README** — replaced emoji headings with inline icons for each extension (Log Capture, Lints, Drift Advisor), copied from sibling projects.
- **New suite icon** — hierarchy diagram icon replacing the previous log-viewer style icon, with SVG source and Python conversion script (`scripts/svg_to_png.py`).

## [1.0.4]

### Added

- **PAT validation with automatic browser fallback** — the publish script checks `VSCE_PAT` (via `vsce verify-pat`) and `OVSX_PAT` before any expensive work. If PATs are missing or invalid (MFA, billing, Azure DevOps org issues), it automatically falls back to browser-based upload: opens the Marketplace management page and highlights the `.vsix` in Explorer so you can drag-and-drop via ⋮ → Update. No flags or CLI knowledge needed.
- **Post-publish verification polling** — after publishing (CLI or browser upload), the script polls the VS Code Marketplace and Open VSX Registry every 15 seconds (up to 5 minutes) until the new version is live, confirming the release actually landed.
- **New modules**: `auth.py` (token validation), `verify_publish.py` (registry polling).

### Changed

- **Improved publish error messages** — `publish_marketplace.py` now detects PAT/auth failures specifically and includes targeted remediation hints instead of a generic "check the log" message.
- **README.md** — updated feature list

## [1.0.3]

### Changed

- **CHANGELOG.md is now the version source of truth** — the publish script reads the first `## [x.y.z]` heading from CHANGELOG.md and automatically syncs package.json to match. The `--patch`, `--minor`, and `--major` flags have been removed.
- **Git commit & push before publish** — the script now commits all outstanding changes and pushes to the remote before publishing. After a successful publish, an annotated `vX.Y.Z` tag is created and pushed.

## [1.0.2]

### Added

- **Screenshots section in README** — added screenshots from all three extensions: Log Capture (log viewer with severity markers, SQL query view), Lints (memory leak detection, AI solver), and Drift Advisor (health check, performance profiler). Images stored locally in `images/screenshots/`.

### Changed

- **CHANGELOG.md is now the version source of truth** — the publish script reads the first `## [x.y.z]` heading from CHANGELOG.md and automatically syncs package.json to match. The `--patch`, `--minor`, and `--major` flags have been removed.
- **Git commit & push before publish** — the script now commits all outstanding changes and pushes to the remote before publishing. After a successful publish, an annotated `vX.Y.Z` tag is created and pushed.
- **README rewritten** — removed publishing workflow and internal dev details. README now focuses on what each extension does, why to install them together, and how to get started.
- **License link** — MIT license text in README is now a clickable link to the LICENSE file.
- **Publishing docs moved to CONTRIBUTING.md** — publish script usage, environment variables, and requirements are now in a separate contributor document.

## [1.0.1]

### Added

- **Open VSX publishing** — publish script now publishes to both the VS Code Marketplace and the Open VSX Registry (used by VS Codium, Gitpod, Eclipse Theia). Controlled via `OVSX_PAT` env var; skippable with `--skip-ovsx`.
- **Auto-update of CLI tools** — vsce and ovsx are automatically updated to the latest version before each publish run, preventing mid-publish "outdated version" warnings.
- **Git integration** — after a successful publish, creates an annotated `vX.Y.Z` git tag.
- **Expanded pre-flight checks:**
  - All required package.json fields (name, displayName, description, version, publisher, license).
  - `engines.vscode` field is present.
  - `categories` includes "Extension Packs".
  - LICENSE file exists on disk and matches the `license` field.
  - `repository.url` is set.
  - Icon is a valid PNG (magic-byte check).
  - `.vscodeignore` file exists to keep the .vsix clean.
  - Extension IDs in `extensionPack` have valid format and no duplicates.
  - Warns if the version is already published on the Marketplace.
  - Warns if a git tag for the version already exists.
  - Verifies Node.js is installed.
- **Colored terminal output** — errors (red), warnings (yellow), success (green), headings (cyan). Respects `NO_COLOR` env var and non-TTY pipes. Windows ANSI support enabled via `SetConsoleMode`.
- **Log files** — every run writes a full plain-text log to `reports/<yyyymmdd>/<yyyymmdd_HHMMSS>_publish.log`.
- `.vscodeignore` to exclude scripts, reports, and dev files from the .vsix package.
- `.gitignore` for .vsix files, reports, and node_modules.
- Contact email (saropa.suite@saropa.com) in README and package metadata.

### Changed

- **Modularized publish script** — split the monolithic `publish.py` into `scripts/modules/` subpackage: `color`, `log`, `npm_tools`, `checks`, `version`, `git`, `packaging`, `publish_marketplace`, `publish_openvsx`.
- Publish script now uses `shell=True` on Windows to resolve `.cmd` wrappers (fixes `FileNotFoundError` when running vsce on Windows).

## [1.0.0]

### Added

- Initial release of the Saropa Suite VS Code extension pack.
- One-click install bundles three Saropa extensions:
  - **Saropa Log Capture** (`saropa.saropa-log-capture`) - debug log tooling.
  - **Saropa Lints** (`saropa.saropa-lints`) - Dart/Flutter lint rules.
  - **Drift Viewer** (`saropa.drift-viewer`) - drift analysis tooling.
- Extension pack icon and marketplace metadata.
- Publish script (`scripts/publish.py`) for automated VSIX packaging and marketplace publishing.
