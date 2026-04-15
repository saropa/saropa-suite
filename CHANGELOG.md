# Changelog

All notable changes to the **Saropa Suite** extension pack will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- cspell:disable -->

## [Unreleased]

### Changed

- **README rewritten** — removed publishing workflow and internal dev details. README now focuses on what each extension does, why to install them together, and how to get started.
- **Publishing docs moved to CONTRIBUTING.md** — publish script usage, environment variables, and requirements are now in a separate contributor document.

## [1.0.1]

### Added

- **Open VSX publishing** — publish script now publishes to both the VS Code Marketplace and the Open VSX Registry (used by VS Codium, Gitpod, Eclipse Theia). Controlled via `OVSX_PAT` env var; skippable with `--skip-ovsx`.
- **Auto-update of CLI tools** — vsce and ovsx are automatically updated to the latest version before each publish run, preventing mid-publish "outdated version" warnings.
- **Git integration** — after a version bump the script commits the package.json change and creates an annotated `vX.Y.Z` tag after successful publish.
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

- **CHANGELOG.md is now the version source of truth** — the publish script reads the first `## [x.y.z]` heading from CHANGELOG.md and automatically syncs package.json to match. The `--patch`, `--minor`, and `--major` flags have been removed.
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
