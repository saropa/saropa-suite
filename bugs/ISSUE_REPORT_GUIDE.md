# Issue Report Guide

<!-- Formerly bugs/BUG_REPORT_GUIDE.md — renamed to the issue-guide format shared with saropa_drift_advisor; numeric BUG-NNN naming replaced by BUG_/PROPOSAL_ descriptive names -->

How to file, investigate, and close bugs in `saropa-suite`. Feature requests are a separate document type — see "Feature requests live in plans/" below.

This project is a **VS Code Extension Pack** — a thin meta-package with no runtime code of its own. It bundles three member extensions via `package.json` → `extensionPack` (`saropa.saropa-log-capture`, `saropa.saropa-lints`, `saropa.drift-viewer`) and ships a Python publish toolchain under `scripts/`. Bugs fall into two kinds, and both live under `bugs/`:

1. **Suite bugs** — a defect in *this* repo: the pack manifest (`package.json` — `extensionPack`, version, marketplace metadata, icon), the publish toolchain (`scripts/publish.py` + `scripts/modules/*.py`), packaging/install of the `.vsix`, or the docs (`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`). Use the [`BUG_` naming](#file-naming) and the [Bug Report Template](#bug-report-template).
2. **Member-extension bugs** — a bug that *surfaces* while the suite is installed but whose defect lives inside one of the three bundled extensions, or in the cross-extension "Better Together" integration. **The member extension is not fixed here** — each is a separate repo with its own `bugs/` guide; see [Confirm Attribution Before Filing](#confirm-attribution-before-filing). Record the referral here with the [Member-Extension Referral Template](#member-extension-referral-template).

**Feature requests live in `plans/`, not `bugs/`.** A feature request is a proposal for future work, not a defect report — it belongs alongside implementation plans. File it as `plans/PROPOSAL_<DESCRIPTION>.md` using the [feature request template](#feature-request-template). Do not create it under `bugs/`.

---

## File Naming

**Bugs** (`bugs/`): every file is a real defect — a manifest error, a publish-toolchain failure, a packaging problem that actually happened. Prefix every filename `BUG_`, then a `SCREAMING_SNAKE_CASE` description. No feature/proposal content belongs here.

| Type | Pattern | Example |
|------|---------|---------|
| Manifest | `BUG_MANIFEST_<DESCRIPTION>.md` | `BUG_MANIFEST_STALE_EXTENSION_ID.md` |
| Publish toolchain | `BUG_PUBLISH_<DESCRIPTION>.md` | `BUG_PUBLISH_VERSION_SYNC_WRONG_HEADING.md` |
| Packaging / install | `BUG_PACKAGING_<DESCRIPTION>.md` | `BUG_PACKAGING_MEMBER_EXTENSION_NOT_INSTALLED.md` |
| Documentation | `BUG_DOCS_<DESCRIPTION>.md` | `BUG_DOCS_README_REMOVED_INTEGRATION.md` |
| Versioning | `BUG_VERSION_<DESCRIPTION>.md` | `BUG_VERSION_CHANGELOG_PACKAGE_MISMATCH.md` |
| Member-extension referral | `REFERRAL_<MEMBER>_<DESCRIPTION>.md` | `REFERRAL_LOG_CAPTURE_DRIFT_LINK_BROKEN.md` |

**Feature requests** (`plans/`): a proposal for work not yet built. Prefix every filename `PROPOSAL_`, then a `SCREAMING_SNAKE_CASE` description. Related proposals share a common leading segment so siblings sort together.

| Type | Pattern | Example |
|------|---------|---------|
| Pack / manifest request | `PROPOSAL_<DESCRIPTION>.md` | `PROPOSAL_ADD_FOURTH_MEMBER_EXTENSION.md` |
| Tooling / infra request | `PROPOSAL_INFRA_<DESCRIPTION>.md` | `PROPOSAL_INFRA_PUBLISH_OPEN_VSX_RETRY.md` |
| Integration request | `PROPOSAL_INTEGRATION_<DESCRIPTION>.md` | `PROPOSAL_INTEGRATION_SHARED_SESSION_CONTEXT.md` |

No numeric IDs in either scheme — the description is the identity. Check existing files before creating (`ls bugs/`, `ls plans/PROPOSAL_*.md`) to avoid duplicates.

---

## Confirm Attribution Before Filing

**Before filing a bug here, prove where the bug lives.** A bug seen while the suite is installed does not mean the defect is in this repo — this repo ships almost no behavior. Most user-visible behavior comes from the three member extensions. A symptom's surface ("Saropa" in the message, the suite icon in the extensions list) is not attribution — it is a label, not a `file:line`.

### Positive attribution (required)

The suite repo owns exactly three things: the **pack manifest** (`package.json`), the **publish toolchain** (`scripts/`), and the **docs**. If the symptom is not in one of those, it is a member-extension bug.

```bash
# Does the suite manifest reference the thing? (extension IDs, version, metadata, icon)
grep -n "extensionPack\|version\|publisher\|icon" package.json

# Is the symptom produced by the publish toolchain?
grep -rn "<symptom keyword>" scripts/
```

Paste the matches (`file:line`) into the report. Zero matches in all three owned areas = do not file here.

**Suite bug — defect is in this repo.** File a [suite bug](#bug-report-template) when the failure is in one of:

- **Pack manifest** — wrong/stale extension ID in `extensionPack`, version mismatch between `CHANGELOG.md` and `package.json`, bad `publisher`/`icon`/`engines`, missing marketplace field.
- **Publish toolchain** — `scripts/publish.py` or a `scripts/modules/*.py` step fails, a pre-flight check is wrong, the `.vsix` packages incorrectly, the version sync or git tag is wrong.
- **Packaging/install** — the `.vsix` installs but does not pull in a member extension; the pack metadata renders wrong on the Marketplace / Open VSX listing.
- **Docs** — `README.md` / `CONTRIBUTING.md` / `CHANGELOG.md` describe the suite incorrectly.

### Negative attribution (required when the symptom is runtime or integration behavior)

If the broken behavior is *runtime* (a log fails to capture, a lint mis-fires, a Drift query view is wrong) or is the *cross-extension integration* (Log Capture not embedding lint findings, "Open in Drift Advisor" right-click missing), the fix belongs in that extension's repo, not here:

| Member extension | Marketplace ID | Repo |
|---|---|---|
| Saropa Log Capture | `saropa.saropa-log-capture` | `D:\src\saropa-log-capture` |
| Saropa Lints | `saropa.saropa-lints` | `D:\src\saropa_lints` |
| Saropa Drift | `saropa.drift-viewer` | `D:\src\saropa_drift_advisor` |

**Confirm it reproduces standalone.** Install only the suspected member extension (not the suite) and reproduce. If it still breaks, it is a member-extension bug — file it in that repo's `bugs/` and record a [referral](#member-extension-referral-template) here. If it only breaks when the *suite* is installed (e.g. an extension-ID conflict the pack introduces), that is a suite bug.

### Reverse case: behavior whose owner is not here

If the positive grep returns nothing and the symptom is runtime behavior, **stop**. Name the suspected member extension, paste the positive grep from that repo, and file the bug in that repo's `bugs/` folder. Do not open a bug here on the theory that "the pack probably causes it somehow" — that guess costs real round-trips.

### Why this section exists

The suite is a wrapper. The default failure mode is logging a member extension's runtime bug here (where there is no code to fix it) or, in reverse, treating a manifest/publish defect as "one of the bundled extensions' problem." The only defense is the standalone-reproduce test plus grep evidence pasted directly in the report.

---

## Bug Report Template

For suite bugs. Copy the block below into a new `bugs/BUG_<AREA>_<DESCRIPTION>.md` file.

````markdown
# BUG: Short, Specific Title

**Status: Open**

<!-- Status values: Open → Investigating → Fix Ready → Closed -->

Created: YYYY-MM-DD
Component: Manifest / Publish Toolchain / Packaging / Integration / Documentation / Versioning
File: `package.json` / `scripts/publish.py` / `scripts/modules/<step>.py` / `README.md` (line ~NNN)
Severity: Critical / High / Medium / Low

---

## Summary

One or two sentences: what happens, what should happen instead.

---

## Attribution Evidence

Grep proof that the defect lives in this repo (manifest / scripts / docs), not in a member extension. If the positive grep is empty, the bug does not belong in this repo — do not file here. See "Confirm Attribution Before Filing" in the guide.

```bash
# Positive — defect IS in a suite-owned file
grep -n "extensionPack\|version\|publisher\|icon" package.json
grep -rn "<symptom keyword>" scripts/
# Expected: file:NN: ... <match> ...

# Negative — behavior is NOT reproducible in a member extension standalone (paste only if the symptom is runtime/integration)
# Expected: standalone member extension works correctly
```

**Owned file(s) — list ALL:** `path/to/file:NN`

If the broken behavior reproduces with only a member extension installed (no suite), this is the wrong template — file upstream and use the [Member-Extension Referral Template](#member-extension-referral-template).

---

## Environment

- OS:
- Suite version (from `CHANGELOG.md` top heading):
- VS Code version:
- vsce / ovsx version (if publish-related):
- Member extensions installed + versions (if integration-related):
- Relevant env vars (`VSCE_PAT` / `OVSX_PAT` set or unset):

---

## Steps to Reproduce

1. Start from a clean state.
2. ...
3. ...

Rules:
- Prefer `python scripts/publish.py --dry-run` — safe to re-run.
- Specify exact commands, not "run the publish."
- For install/packaging bugs, give the install command and what the extensions list shows, e.g. `code --install-extension saropa-suite-X.Y.Z.vsix` → ACTUAL: only 2 of 3 member extensions installed — EXPECTED: all 3.
- If the bug is intermittent, say so and estimate how often.

**Frequency:** Always / Only on publish / Only on fresh install / Intermittent

---

## Expected Behavior

[What should happen]

---

## Actual Behavior

[What actually happens]

---

## Error Output

Include ALL of the following that exist. Do not summarize or truncate.

### Terminal / Command Output

Paste the full output of the command you ran, including the command itself and any pre-flight check results.

### Stack Traces

If a Python step raised, copy the full traceback. Screenshot alone is not enough because stack traces need to be searchable.

---

## Screenshots / Recordings

- **Annotate screenshots.** Circle or arrow the relevant area (Marketplace listing, extensions list).
- **Before and after** if the bug is visual.

---

## Minimal Reproducible Example

Strip down the scenario to the absolute minimum that still triggers the bug — the shortest command sequence or the smallest `package.json` excerpt that fails. The goal: someone else can copy-paste it and see the bug within 60 seconds.

---

## What I Already Tried

- [ ] Ran `python scripts/publish.py --dry-run`
- [ ] Tested a fresh install of the `.vsix`
- [ ] Tested the member extension standalone
- [Other attempts and their results]

---

## Regression Info

- Last working version:
- First broken version:
- What changed:

---

## Root Cause

<!-- Fill in during investigation. Explain the *mechanism*: which manifest field,
     which pre-flight check, or which script branch evaluates wrong, and why.
     Reference specific files and lines. -->

---

## Suggested Fix

<!-- Describe the change to the manifest, the publish step, or the doc.
     Prefer extending an existing pre-flight check / module over adding a new one. -->

---

## Changes Made

<!-- Fill in when a fix is written. Show before/after for each touched file. -->

---

## Commits

<!-- Add commit hashes as fixes land. -->
- `abcdef0` fix: description

---

## Impact

- Who is affected:
- What is blocked:
- Data risk:
- Frequency:
````

---

## Member-Extension Referral Template

For recording that a reported bug belongs to a bundled extension (or the cross-extension integration) and was referred upstream. Copy into a new `bugs/REFERRAL_<MEMBER>_<DESCRIPTION>.md` file.

````markdown
# REFERRAL: <member extension> — short description

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

## Feature Request Template

**File this under `plans/`, not `bugs/`** — see "Feature requests live in plans/" above. Copy the block below into a new `plans/PROPOSAL_<DESCRIPTION>.md` file.

````markdown
# PROPOSAL: Short, Specific Title

**Status: Open**

<!-- Status values: Open → Accepted → In Progress → Closed -->
<!-- Use "Declined" if rejected, with rationale in the Decision section -->

Created: YYYY-MM-DD
Type: Pack manifest / Publish tooling / Integration / Documentation
Related: member extension(s) or existing plan/bug files, if any

---

## Summary

One or two sentences: what the feature does and why it matters.

---

## Motivation

Why this feature is needed. Include concrete examples from real usage where this would have prevented a bad publish, improved the install experience, or saved developer time.

---

## Behavior

<!-- For manifest changes: describe the extensionPack / metadata change -->
<!-- For publish tooling: describe the new pre-flight check or step and its input/output -->
<!-- For integration: name BOTH extensions and which side owns the hook -->

---

## Edge Cases

1. **Case description** — should handle / should ignore / needs discussion
2. ...

---

## Alternatives Considered

---

## Decision

<!-- Fill in when the proposal is accepted or declined -->

---

## Implementation Notes

<!-- Fill in when work begins -->

---

## Commits

<!-- Add commit hashes as implementation lands -->
- `abcdef0` feat: description
````

---

## What Makes a Good Bug Report

### Title

- Start with `BUG:` and the area: `` BUG: extensionPack — ... ``
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

**How to report:** Create `bugs/BUG_MANIFEST_<DESCRIPTION>.md`, copy the [Bug Report Template](#bug-report-template), and complete **Steps to Reproduce** plus **Attribution Evidence** (grep).

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

## Feature Request Categories

### Pack / Manifest Request

A change to the bundled member set or pack metadata (add/remove a member extension, new marketplace field).

**How to report:** Create `plans/PROPOSAL_<DESCRIPTION>.md`, copy the [Feature Request Template](#feature-request-template).

**Evaluation criteria:**
- Does the extension exist on both the Marketplace and Open VSX?
- Does it fit the "Better Together" story, or is it unrelated bloat?

### Tooling / Infrastructure Request

Improvements to the publish toolchain, pre-flight checks, or packaging.

**How to report:** Create `plans/PROPOSAL_INFRA_<DESCRIPTION>.md` and describe the current behavior, desired behavior, and motivation.

**Evaluation criteria:**
- Can it extend an existing pre-flight check / module rather than add a parallel one?
- Does it keep `--dry-run` safe (no auth, no publish)?

### Integration Request

A new cross-extension capability.

**How to report:** Create `plans/PROPOSAL_INTEGRATION_<DESCRIPTION>.md`; name both extensions and which owns the hook. The implementation lands in the member repos, not here.

---

## Investigation Checklist

Use this when diagnosing a new bug.

- [ ] **Positive attribution grep** — grep `package.json` and `scripts/` for the symptom; at least one match, pasted in the report. Zero matches = do not file here
- [ ] **Negative attribution** — if the symptom is runtime/integration behavior, reproduce it with the member extension standalone; it is likely a referral, not a suite bug
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
| Attributing a symptom by its label | "Saropa" in a message or the suite icon does not mean the defect is in this repo | Attribution is `file:line` in `package.json` / `scripts/` / docs, not a label |
| Stale / typo'd ID in `extensionPack` | The pack silently installs only the IDs that resolve | Each ID must exactly match a published Marketplace ID |
| Version drift CHANGELOG ↔ package.json | The publish syncs to the wrong build | `CHANGELOG.md` top heading is the single source; derive the rest |
| `icon` not a valid PNG | Marketplace rejects or renders blank | Validate the PNG (the publish pre-flight checks this) |
| Publishing without a PAT | `VSCE_PAT` / `OVSX_PAT` missing → publish step fails late | Check env vars before publish; `--dry-run` skips auth |
| Treating a "Better Together" gap as a suite bug | The hook lives in a member extension (producer or consumer) | Name both extensions; fix the owning side upstream |
| Editing a member extension's repo without permission | Cross-project edits are out of scope for this repo | File the bug in that repo; do not edit it from here |
| Bundling files `.vscodeignore` should exclude | Bloats the `.vsix` or ships scratch files | Verify `.vscodeignore`; re-package and inspect size |

---

## Fix Requirements

Every bug fix must satisfy these before it can be closed.

### Code

- [ ] Fix addresses the **root cause** (the manifest field, the publish step, the doc), not just the symptom
- [ ] Fix includes a comment (in the Python step) explaining what was wrong and why the new code is correct
- [ ] Extends an existing pre-flight check / module rather than adding a parallel one
- [ ] No member-extension repo was edited from here (referrals only)

### Verification

The suite has no unit tests; verification is the dry-run publish path plus a real install.

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

### Bugs

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

### Feature Requests

```
Open
  │
  ├──► Declined     ← rejected with rationale, file moved to history
  │
  ▼
Accepted            ← approved, scope decided
  │
  ▼
In Progress         ← implementation underway
  │
  ▼
Closed              ← merged, verified, file moved to history
```

### Moving to History

When a bug is closed (or a proposal is declined), `git mv` its file into the shared history root — the same `plans/history/` tree used for closed plans, not a separate `bugs/history/`:

```
bugs/BUG_AREA_DESCRIPTION.md
  → plans/history/YYYY.MM/YYYY.MM.DD/BUG_AREA_DESCRIPTION.md

plans/PROPOSAL_DESCRIPTION.md
  → plans/history/YYYY.MM/YYYY.MM.DD/PROPOSAL_DESCRIPTION.md
```

Use the date the issue was closed. Create the `YYYY.MM/YYYY.MM.DD` folders if they do not exist (matches the existing `plans/history/2026.06/2026.06.13/` layout). Grep and repoint any `bugs/<file>.md` or `plans/<file>.md` references (CHANGELOG, other issue/plan files) to the new path in the same commit.

---

## Severity Guide

| Severity | Meaning | Examples |
|----------|---------|---------|
| Critical | Publishes a broken pack, or a fresh install is missing a member extension | Stale `extensionPack` ID, version published from the wrong CHANGELOG heading, publish toolchain crashes mid-publish |
| High | Publish/install works but is wrong in a way that forces a workaround | Wrong `engines` range blocks install on current VS Code, pre-flight check passes when it should fail |
| Medium | Publish/install works but is wrong in a recoverable way | Marketplace metadata renders wrong, a pre-flight check passes when it should warn, docs describe a removed integration |
| Low | Cosmetic or doc-only, no install/publish impact | README typo, changelog wording, stale screenshot |

---

## Linking

- Reference bugs from commits: `fix: description (BUG_AREA_DESCRIPTION)`
- Reference proposals from commits: `feat: description (PROPOSAL_DESCRIPTION)`
- Reference issues from docs: `[issue file](bugs/BUG_AREA_DESCRIPTION.md)` or `[proposal](plans/PROPOSAL_DESCRIPTION.md)`
- Reference referrals: `Referred upstream: bugs/REFERRAL_MEMBER_DESCRIPTION.md`
- Reference related history: `Related: plans/history/YYYY.MM/YYYY.MM.DD/filename.md`

---

## Policy Note

Do not log project-specific findings or proposals directly in this guide.

- This file is process documentation only.
- Every concrete bug must live in a separate `BUG_*` file under `bugs/`; every feature request must live in a separate `PROPOSAL_*` file under `plans/` — using the naming rules above.
- If you discover this happened again, move the content into dedicated issue files immediately and leave only this policy note.
