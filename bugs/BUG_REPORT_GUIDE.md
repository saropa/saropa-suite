# Bug Report Guide

How to file, investigate, and close bugs in `saropa-suite`.

This project is a **VS Code Extension Pack** — a thin meta-package with no runtime code of its own. It bundles three member extensions via `package.json` → `extensionPack` (`saropa.saropa-log-capture`, `saropa.saropa-lints`, `saropa.drift-viewer`) and ships a Python publish toolchain under `scripts/`. Bugs fall into two kinds, and both live under `bugs/`:

1. **Suite bugs** — a defect in *this* repo: the pack manifest (`package.json` — `extensionPack`, version, marketplace metadata, icon), the publish toolchain (`scripts/publish.py` + `scripts/modules/*.py`), packaging/install of the `.vsix`, or the docs (`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`). Use the [`BUG-NNN-...` naming](#file-naming) and the [Bug Report Template](#bug-report-template).
2. **Member-extension bugs** — a bug that *surfaces* while the suite is installed but whose defect lives inside one of the three bundled extensions, or in the cross-extension "Better Together" integration. **The member extension is not fixed here** — each is a separate repo with its own `bugs/` guide; see [Attribution: suite bug vs member extension](#attribution-suite-bug-vs-member-extension). Record the referral here with the [Member-Extension Referral Template](#member-extension-referral-template).

---

## File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Suite bug | `BUG-NNN-area-short-description.md` | `BUG-010-extensionPack-stale-extension-id.md` |
| Member-extension referral | `referral_member_short-description.md` | `referral_log-capture_drift-link-broken.md` |

Use lowercase with underscores/hyphens. `NNN` is the next free number (check the highest existing `BUG-NNN-*` file). Check existing files before creating.

---

## Attribution: suite bug vs member extension

**Before filing, prove where the bug lives.** A bug seen while the suite is installed does not mean the defect is in this repo — this repo ships almost no behavior. Most user-visible behavior comes from the three member extensions. A symptom's surface ("Saropa" in the message, the suite icon in the extensions list) is not attribution.

### The decisive test

The suite repo owns exactly three things: the **pack manifest** (`package.json`), the **publish toolchain** (`scripts/`), and the **docs**. If the symptom is not in one of those, it is a member-extension bug.

```bash
# Does the suite manifest reference the thing? (extension IDs, version, metadata, icon)
grep -n "extensionPack\|version\|publisher\|icon" package.json

# Is the symptom produced by the publish toolchain?
grep -rn "<symptom keyword>" scripts/
```

### Suite bug — defect is in this repo

File a [suite bug](#bug-report-template) here when the failure is in one of:

- **Pack manifest** — wrong/stale extension ID in `extensionPack`, version mismatch between `CHANGELOG.md` and `package.json`, bad `publisher`/`icon`/`engines`, missing marketplace field.
- **Publish toolchain** — `scripts/publish.py` or a `scripts/modules/*.py` step fails, a pre-flight check is wrong, the `.vsix` packages incorrectly, the version sync or git tag is wrong.
- **Packaging/install** — the `.vsix` installs but does not pull in a member extension; the pack metadata renders wrong on the Marketplace / Open VSX listing.
- **Docs** — `README.md` / `CONTRIBUTING.md` / `CHANGELOG.md` describe the suite incorrectly.

### Member-extension bug — defect is upstream

If the broken behavior is *runtime* (a log fails to capture, a lint mis-fires, a Drift query view is wrong) or is the *cross-extension integration* (Log Capture not embedding lint findings, "Open in Drift Advisor" right-click missing), the fix belongs in that extension's repo, not here:

| Member extension | Marketplace ID | Repo |
|---|---|---|
| Saropa Log Capture | `saropa.saropa-log-capture` | `D:\src\saropa-log-capture` |
| Saropa Lints | `saropa.saropa-lints` | `D:\src\saropa_lints` |
| Saropa Drift Advisor | `saropa.drift-viewer` | `D:\src\saropa_drift_advisor` |

**Confirm it reproduces standalone.** Install only the suspected member extension (not the suite) and reproduce. If it still breaks, it is a member-extension bug — file it in that repo's `bugs/` and record a [referral](#member-extension-referral-template) here. If it only breaks when the *suite* is installed (e.g. an extension-ID conflict the pack introduces), that is a suite bug.

### Why this section exists

The suite is a wrapper. The default failure mode is logging a member extension's runtime bug here (where there is no code to fix it) or, in reverse, treating a manifest/publish defect as "one of the bundled extensions' problem." The only defense is the standalone-reproduce test plus grep evidence pasted directly in the report.

---

## Bug Report Template

For suite bugs. Copy the block below into a new `BUG-NNN-...md` file.

````markdown
# BUG-NNN: <area> — Short, Specific Title

**File:** `package.json` / `scripts/publish.py` / `scripts/modules/<step>.py` / `README.md`
**Severity:** 🔴 High / 🟡 Medium / 🟢 Low
**Category:** Manifest / Publish Toolchain / Packaging / Integration / Documentation / Versioning
**Status:** Open

<!-- Status values: Open → Investigating → Fix Ready → Closed -->

---

## Summary

One or two sentences: what happens, what should happen instead.

---

## Attribution Evidence

Proof that the defect lives in this repo (manifest / scripts / docs), not in a member extension. See "Attribution" in the guide.

```bash
grep -n "extensionPack\|version\|publisher\|icon" package.json
# or:
grep -rn "<symptom keyword>" scripts/
```

If the broken behavior reproduces with only a member extension installed (no suite), this is the wrong template — file upstream and use the [Member-Extension Referral Template](#member-extension-referral-template).

---

## Reproduction

Minimal, exact steps that trigger the bug. This is the single most important section.

```text
# e.g.
1. python scripts/publish.py --dry-run
2. Observe: pre-flight check "<name>" reports <X>
   ACTUAL: <wrong outcome> — EXPECTED: <correct outcome>
```

For install/packaging bugs, give the install command and what the extensions list shows:

```text
code --install-extension saropa-suite-X.Y.Z.vsix
# ACTUAL: only 2 of 3 member extensions installed — EXPECTED: all 3
```

**Frequency:** Always / Only on publish / Only on fresh install / Intermittent

---

## Expected vs Actual

| | Behavior |
|---|---|
| **Expected** | ... |
| **Actual** | ... |

---

## Root Cause

<!-- Fill in during investigation. Explain the *mechanism*: which manifest field,
     which pre-flight check, or which script branch evaluates wrong, and why.
     Reference specific files and lines. -->

```text
# package.json line NN  /  scripts/modules/<step>.py ~line NN
# Show the offending field/code and annotate the defect.
```

---

## Impact

- Who hits this and when (publishing, fresh install, Marketplace render, a specific debug-adapter session).
- Why the failure mode matters (a silently dropped member extension breaks the whole "Better Together" promise; a version mismatch publishes the wrong build).

---

## Suggested Fix

```text
# Describe the change to the manifest, the publish step, or the doc.
# Prefer extending an existing pre-flight check / module over adding a new one.
```

---

## Verification

How the fix is proven. The suite has no unit tests; verification is the dry-run publish path plus a real install.

```bash
python scripts/publish.py --dry-run    # validate + package, no publish
code --install-extension saropa-suite-X.Y.Z.vsix   # confirm all 3 pull in
```

---

## Changes Made

<!-- Fill in when a fix is written. -->

### `package.json` (line NN)  /  `scripts/modules/<step>.py` (line NN)

**Before:**
```text
old
```

**After:**
```text
new
```

---

## Commits

<!-- Add commit hashes as fixes land. -->
- `abcdef0` fix: description

---

## Environment

- Suite version (from `CHANGELOG.md` top heading):
- VS Code version:
- vsce / ovsx version (if publish-related):
- Member extensions installed + versions (if integration-related):
````

---

## Member-Extension Referral Template

For recording that a reported bug belongs to a bundled extension (or the cross-extension integration) and was referred upstream. Copy into a new `referral_member_short-description.md` file.

````markdown
# referral: <member extension> — short description

## Member extension

- Name + Marketplace ID: e.g. Saropa Log Capture (`saropa.saropa-log-capture`)
- Upstream repo: e.g. `D:\src\saropa-log-capture`

## Standalone reproduction

Proof the defect is upstream, not in the suite: it reproduces with ONLY the member
extension installed (suite uninstalled).

```text
1. Uninstall the suite. Install only <member extension>.
2. <steps>
   → still broken ⇒ member-extension bug (this referral is correct)
```

If it only breaks with the suite installed, STOP — it is a suite bug; use the Bug Report Template instead.

## Disposition

- **Filed upstream:** path to the bug file in the member repo's `bugs/`, or the issue link.
- **Integration note:** if this is a "Better Together" cross-extension bug, name BOTH extensions and which one owns the missing hook (the producer or the consumer of the API).
- **Suite action, if any:** usually none. Only when the pack must bump a member's `extensionPack` ID or minimum version does the suite change at all.
````

---

## What Makes a Good Bug Report

### Title

- Start with the bug number and area: `` BUG-NNN: extensionPack — ... ``
- Classify the failure: "stale extension ID", "version mismatch", "icon fails PNG validation", "member extension not installed"
- Be specific: "publish syncs `package.json` to the wrong CHANGELOG heading" beats "publish broken"

### Reproduction

- **Smallest exact command sequence** that triggers it — prefer `--dry-run` so it is safe to re-run
- Mark expected vs actual inline
- Name the trigger context (publish, fresh install, Marketplace render, a specific debug adapter)
- For integration bugs, state which member extensions were installed and their versions

### Root Cause

- Explain the **mechanism**: which manifest field, which pre-flight check, or which `scripts/modules/*.py` branch is wrong, and why
- Reference specific files and line numbers
- Name the trigger class (version drift, ID typo, missing PAT, fresh-install vs upgrade)

---

## Bug Categories

### Manifest

`package.json` is wrong: a stale/typo'd ID in `extensionPack`, mismatched `version`, bad `publisher` / `icon` / `engines`, or a missing marketplace field.

**Investigation focus:**
- Does each `extensionPack` ID exactly match a published Marketplace ID?
- Does `version` match the top `## [x.y.z]` heading in `CHANGELOG.md`?
- Is `icon` a valid PNG at the referenced path?

### Publish Toolchain

`scripts/publish.py` or a `scripts/modules/*.py` step fails or does the wrong thing.

**Investigation focus:**
- Which pre-flight check fired (or failed to fire when it should have)?
- Did `--dry-run` succeed but a publish-only step (Marketplace / Open VSX auth, git tag) fail?
- Is the version read from `CHANGELOG.md` and synced to `package.json` correctly?

### Packaging

The `.vsix` is built but installs wrong.

**Investigation focus:**
- Does installing the `.vsix` pull in all three member extensions?
- Is anything bundled that `.vscodeignore` should have excluded (or vice versa)?

### Integration ("Better Together")

A cross-extension API described in the README does not work (Log Capture not embedding lint findings, "Open in Drift Advisor" right-click missing, session metadata not carrying DB context).

**Investigation focus:**
- Reproduce with each member extension standalone — which side owns the hook (producer vs consumer)?
- This is almost always a **member-extension** referral, not a suite code change.

### Documentation

The suite docs describe the suite incorrectly.

**Investigation focus:**
- Does `README.md` list the right member extensions and integrations?
- Does `CONTRIBUTING.md` match the actual publish flow and env vars?

### Versioning

Version drift between `CHANGELOG.md`, `package.json`, the `.vsix` filename, and the git tag.

**Investigation focus:**
- Is `CHANGELOG.md`'s top `## [x.y.z]` the single source of truth, with everything derived from it?

---

## Investigation Checklist

Use this when diagnosing a new bug.

- [ ] **Attribution** — is the symptom in the manifest (`package.json`), the publish toolchain (`scripts/`), or the docs? If it is runtime/integration behavior, reproduce it with the member extension standalone — it is likely a referral, not a suite bug
- [ ] **Reproduce it** — capture the exact command / install steps; prefer `python scripts/publish.py --dry-run` (safe to re-run)
- [ ] **Read the source** — open the offending `package.json` field or `scripts/modules/*.py` step and trace it
- [ ] **Check the version chain** — `CHANGELOG.md` top heading → `package.json` `version` → `.vsix` name → git tag all agree
- [ ] **Check the IDs** — every `extensionPack` ID matches a live Marketplace listing
- [ ] **Run the dry run** — `python scripts/publish.py --dry-run` to confirm current behavior without publishing
- [ ] **Test a real install** — `code --install-extension saropa-suite-X.Y.Z.vsix` and confirm all three member extensions appear

---

## Common Pitfalls

These patterns have caused bugs before. Check for them during investigation.

| Pitfall | Why It Breaks | Correct Pattern |
|---------|---------------|-----------------|
| Logging a member extension's runtime bug here | The suite has no runtime code to fix it | Reproduce standalone; file upstream + record a referral |
| Stale / typo'd ID in `extensionPack` | The pack silently installs only the IDs that resolve | Each ID must exactly match a published Marketplace ID |
| Version drift CHANGELOG ↔ package.json | The publish syncs to the wrong build | `CHANGELOG.md` top heading is the single source; derive the rest |
| `icon` not a valid PNG | Marketplace rejects or renders blank | Validate the PNG (the publish pre-flight checks this) |
| Publishing without a PAT | `VSCE_PAT` / `OVSX_PAT` missing → publish step fails late | Check env vars before publish; `--dry-run` skips auth |
| Treating a "Better Together" gap as a suite bug | The hook lives in a member extension (producer or consumer) | Name both extensions; fix the owning side upstream |
| Editing a member extension's repo without permission | Cross-project edits are out of scope for this repo | File the bug in that repo; do not edit it from here |
| Bundling files `.vscodeignore` should exclude | Bloats the `.vsix` or ships scratch files | Verify `.vscodeignore`; re-package and inspect size |

---

## Fix Requirements

Every suite bug fix must satisfy these before it can be closed.

### Change

- [ ] Fix addresses the **root cause** (the manifest field, the publish step, the doc), not just the symptom
- [ ] Fix includes a comment (in the Python step) explaining what was wrong and why the new code is correct
- [ ] Extends an existing pre-flight check / module rather than adding a parallel one
- [ ] No member-extension repo was edited from here (referrals only)

### Verification

- [ ] `python scripts/publish.py --dry-run` — validate + package succeeds with zero pre-flight failures
- [ ] For install/packaging bugs: `code --install-extension saropa-suite-X.Y.Z.vsix` pulls in all three member extensions
- [ ] For versioning bugs: `CHANGELOG.md` heading, `package.json` version, `.vsix` name, and git tag all agree

### Documentation

- [ ] `CHANGELOG.md` updated under the current top `## [x.y.z]` heading → `### Fixed`
- [ ] `README.md` / `CONTRIBUTING.md` updated if the integration set, member list, or publish flow changed
- [ ] Bug report file updated with root cause, changes, and commit hashes
- [ ] Status updated to `Closed`

---

## Lifecycle

```
Open
  │
  ▼
Investigating       ← actively diagnosing, root cause section being filled in
  │
  ▼
Fix Ready           ← change written, dry-run clean, awaiting commit
  │
  ▼
Closed              ← merged, verified, file moved to history
```

### Moving to History

When a bug is closed, move its file:

```
bugs/BUG-NNN-area-description.md
  → bugs/history/YYYYMMDD/BUG-NNN-area-description.md
```

Use the date the bug was closed (`YYYYMMDD`, matching the `reports/` folder convention). Create the date folder if it does not exist.

---

## Severity Guide

| Severity | Meaning | Examples |
|----------|---------|---------|
| 🔴 High | Publishes a broken pack, or a fresh install is missing a member extension | Stale `extensionPack` ID, version published from the wrong CHANGELOG heading, publish toolchain crashes mid-publish |
| 🟡 Medium | Publish/install works but is wrong in a recoverable way | Marketplace metadata renders wrong, a pre-flight check passes when it should warn, docs describe a removed integration |
| 🟢 Low | Cosmetic or doc-only, no install/publish impact | README typo, changelog wording, stale screenshot |

---

## Linking

- Reference bugs from commits: `fix: description (BUG-NNN)`
- Reference bugs from docs: `[bug file](bugs/BUG-NNN-area-description.md)`
- Reference referrals: `Referred upstream: bugs/referral_member_description.md`
- Reference related history: `Related: bugs/history/YYYYMMDD/filename.md`

---

## Policy Note

Do not log project-specific bug findings directly in this guide.

- This file is process documentation only.
- Every concrete issue must live in a separate file under `bugs/` using the naming rules above.
- If you discover this happened, move the content into dedicated bug files immediately and leave only this policy note.
