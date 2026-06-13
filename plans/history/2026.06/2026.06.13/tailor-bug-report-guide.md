# Tailor Bug Report Guide to the Suite

The bug-report process guide under `bugs/BUG_REPORT_GUIDE.md` was copied verbatim from `saropa_dart_utils`, a Dart utility library, and described that project's concerns — `lib/` extension methods, dartdoc contracts, grapheme-cluster edge cases, `dart test`, and a "library bug vs consumed `saropa_lints` dependency" attribution split. None of that applies to `saropa-suite`, which is a VS Code **Extension Pack**: a thin meta-package with no runtime code that bundles three member extensions via `package.json` → `extensionPack` and ships a Python publish toolchain under `scripts/`. The guide was rewritten so its taxonomy, templates, attribution logic, and quality gates match the suite's actual structure.

## Finish Report (2026-06-13)

### Scope

(C) docs only — a single Markdown process document. No code, manifest, or script changed.

### What changed

`bugs/BUG_REPORT_GUIDE.md` was retargeted end to end:

- **Two bug kinds redefined.** "Library bug vs consumed dependency" became **Suite bug** (defect in the pack manifest `package.json`, the publish toolchain `scripts/`, or the docs) vs **Member-extension bug** (defect inside one of the three bundled extensions or in the cross-extension "Better Together" integration, fixed upstream in its own repo).
- **Attribution section rebuilt around the standalone-reproduce test.** The decisive question is whether the symptom reproduces with only a member extension installed (suite uninstalled) — if so it is a member-extension referral, not a suite bug. A table maps each member to its Marketplace ID and repo: Log Capture (`saropa.saropa-log-capture`, `D:\src\saropa-log-capture`), Lints (`saropa.saropa-lints`, `D:\src\saropa_lints`), Drift Advisor (`saropa.drift-viewer`, `D:\src\saropa_drift_advisor`).
- **Templates replaced.** The Dart "Bug Report Template" became a suite template keyed to manifest/toolchain/packaging/docs fields. The "Lint Exclusion Template" became a "Member-Extension Referral Template" recording the upstream filing plus the standalone-reproduce proof.
- **Verification path swapped.** Dart specifics (`lib/`, dartdoc, `dart test`, `dart analyze`, grapheme clusters, leap years, scientific notation) were replaced by the suite's real gates: `python scripts/publish.py --dry-run` (validate + package, no publish) and `code --install-extension saropa-suite-X.Y.Z.vsix` (confirm all three members pull in).
- **Categories, pitfalls, severity, and checklist** were retargeted to manifest IDs, version drift (`CHANGELOG.md` top `## [x.y.z]` heading as single source of truth), PNG icon validation, missing `VSCE_PAT` / `OVSX_PAT`, integration ownership (producer vs consumer of an API), and `.vscodeignore` bundling.
- **History folder convention** kept as `YYYYMMDD` to match the existing `reports/` sibling format in this repo.

### Verification

- Member repo paths and Marketplace IDs verified against the filesystem (`D:\src\saropa-log-capture`, `D:\src\saropa_lints`, `D:\src\saropa_drift_advisor` all present) and against `package.json` → `extensionPack`.
- The Drift member's repo name was corrected from a placeholder (`saropa-drift-viewer`) to the actual repo `saropa_drift_advisor` after the canonical URL was supplied.
- The version-source claim (`CHANGELOG.md` top heading drives `package.json`) was confirmed against `CONTRIBUTING.md` and the publish script's documented behavior.
- No automated tests exist in this repo (an extension pack has no test suite); nothing to run.

### Outstanding

- `.vscodeignore` excludes `scripts/`, `reports/`, and `CHANGELOG.md` but not `bugs/`. Committing the `bugs/` directory therefore ships the process guide inside the `.vsix`. Adding `bugs/**` to `.vscodeignore` is a separate decision, not part of this doc-tailoring task.
