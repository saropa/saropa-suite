# README sync with component changelogs

The Saropa Suite README's per-extension feature lists had drifted behind the
shipped feature sets recorded in the three component changelogs. The Saropa Log
Capture section omitted two significant capabilities that had already shipped —
the Firebase Crashlytics & Vitals panel (released in Log Capture 8.1.0/8.1.1)
and the interactive Session Flow Map (released in 8.0.5) — so the suite's
marketing overview undersold Log Capture. The Drift Advisor security bullet also
listed loopback-only binding and CORS control as plain capabilities without
conveying that they are now the secure default (the Drift Advisor Unreleased
section makes both the default via a breaking change).

A review of the Unreleased sections of all three changelogs (Log Capture,
Saropa Lints, Saropa Drift Advisor) found the Unreleased changes themselves to
be fixes and polish that do not warrant README changes; the README gaps trace to
earlier shipped releases surfaced during the changelog review.

## Finish Report (2026-06-13)

### Scope

Docs only (C). No Flutter/Dart app code, no VS Code extension TypeScript, no
tests. The change set edits the suite repository's `README.md` (product feature
overview) and `CHANGELOG.md` (release log).

### Changes

`README.md`:

- Added a **Crashlytics & Vitals panel** bullet to the Log Capture feature list:
  Firebase Crashlytics issues plus Google Play crash-free users/sessions,
  per-issue trend sparklines, "Regressed"/"Repetitive" tags, issue archiving,
  background new-crash alerts, and Firebase issue deep-links.
- Extended the Log Capture **session management** bullet to name 2-or-3-log
  comparison and the interactive Session Flow Map diagram (pan/zoom, per-node
  detail).
- Rewrote the Drift Advisor **Security** bullet to lead with secure-by-default
  (loopback-only binding, no wildcard CORS) instead of presenting those as
  ordinary options.

`CHANGELOG.md`:

- Added an `## [Unreleased]` section with a single Changed entry recording the
  README feature-list update.

The Saropa Lints README section required no change: its Unreleased Package
Vibrancy additions (diamond/constrained/pinned/cross-project-drift explanations)
fall under the existing "version-gap PR triage / dependency health" bullet, and
the rule count (2,100+) remains accurate.

### Verification

The three component changelogs were read directly from their source
repositories (`saropa-log-capture`, `saropa_lints`, `saropa_drift_advisor`) and
each Unreleased section plus recent shipped releases were compared against the
corresponding README feature list. No automated tests exist for the suite
README/CHANGELOG; the change is prose only and introduces no executable
behavior.

### Outstanding

None. The README now reflects the shipped feature sets of all three components.
