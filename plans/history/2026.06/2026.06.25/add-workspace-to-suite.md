# Add Saropa Workspace to the suite

The Saropa Suite extension pack bundled three members (Log Capture, Lints, Drift
Advisor) but omitted Saropa Workspace, a project-aware file/script launcher that
shipped separately. This change adds Workspace as the fourth pack member so the
one-click suite install includes it.

## Finish Report (2026-06-25)

### Scope

Docs and manifest only (variant C). No Flutter/Dart app code and no VS Code
extension TypeScript was touched — the suite repo is an extension *pack* (a
`package.json` manifest plus README/CHANGELOG and a Python publish script). The
member extension itself lives in its own repo (`D:\src\saropa_workspace`) and was
not modified.

### Background

`plans/SPEC_saropa_workspace.md` proposed Workspace as a fourth member and
deliberately deferred the manifest change to the suite maintainer ("requires
explicit approval — not done here"). That approval was given, so the deferred
step was executed.

### Changes

- **`package.json`** — appended `saropa.saropa-workspace` to `extensionPack`
  (kept last; existing three members were not reordered). Updated `description`
  to name Workspace; added `workspace` and `favorites` keywords. The Marketplace
  id `saropa.saropa-workspace` matches the spec.
- **`README.md`** — intro count three → four; added a "Saropa Workspace" entry
  under "What's Included" (appended after Drift Advisor); added a
  "Workspace + the suite" bullet to "Better Together"; added a Workspace launcher
  box to the ASCII architecture diagram feeding the suite; "All three" → "All
  four" in Getting Started.
- **`images/icon_saropa_workspace.png`** — copied from the Workspace repo's
  256px icon, matching the inline-icon convention used by the other three member
  sections (referenced at `width="28"`).
- **`CHANGELOG.md`** — new release section documenting the addition.

### Accuracy note

The "Better Together" bullet describes Workspace's real capability (pinning the
other tools' entry points as one-click favorites) rather than asserting a built
cross-extension API. The spec lists deeper Workspace↔member integrations as
candidates, not commitments; the copy was kept to what ships today to avoid
overstating shipped functionality.

### Version

`package.json` version and the CHANGELOG top heading were promoted to `1.0.8`.
The publish script treats the first `## [x.y.z]` CHANGELOG heading as the version
source of truth and syncs `package.json` to it at publish time.

### Verification

- `package.json` parses as valid JSON.
- The README reference to `images/icon_saropa_workspace.png` resolves to the
  copied asset.
- No test suite exists in this repo (manifest/docs package); nothing to run.
- The extension is not packaged/published here — release is a separate,
  maintainer-run `scripts/publish.py` step.
