# Spec: Saropa Workspace (proposed suite member)

Specification for adding **Saropa Workspace** as a fourth member extension of the
Saropa Suite. This document is a proposal/spec only; it does not change the suite
manifest. Adding the extension to `package.json` → `extensionPack` is a separate,
explicitly-approved step (see "Suite integration" below).

- **Repo:** `D:\src\saropa_workspace` — `https://github.com/saropa/saropa_workspace`
- **Planned Marketplace id:** `saropa.saropa-workspace`
- **Publisher:** `saropa` · **License:** MIT
- **Stack:** TypeScript + esbuild VS Code extension (no Dart, no runtime service).

---

## 1. Purpose

File and script shortcuts for VS Code. Pin any file as a favorite; **single-click
opens** it, **double-click executes** it. The extension turns the project's
scripts and key files into one-action shortcuts from a dedicated sidebar.

It fills a gap the other three suite members do not cover: the suite analyzes,
logs, and profiles, but none of them give the developer a fast, project-aware
launcher for the project's own scripts and important files.

---

## 2. Feature set

### Pinning
- Pin any file from the Explorer context menu or the editor title menu.
- Two scopes:
  - **Project pins** — stored in `<folder>/.vscode/saropa-workspace.json` with
    workspace-relative paths, so they are shareable through the repo.
  - **Global pins** — stored in extension `globalState`, synced via VS Code
    Settings Sync, with absolute paths.
- **Auto-pins** — common project files (default `pubspec.yaml`,
  `analysis_options.yaml`, configurable) are surfaced automatically; removable,
  and removal persists; restorable on demand.
- **Import** — detects and imports existing `.favorites.json` files (the
  kdcro101 "Favorites" format), with a one-time per-workspace prompt. Designed to
  extend to other favorites/bookmark formats.

### Open vs run
- Single-click opens the file in an editor.
- Double-click (within a configurable window) runs it. Because VS Code tree views
  have no native double-click event, an inline play button and a context-menu
  **Run** are provided as the reliable run path; double-click is the convenience
  layer on top.

### Script execution
- Per-pin execution config: command prefix (e.g. `python`), CLI args, working
  directory, environment variables.
- Default command prefix is inferred per file extension when none is set
  (configurable map; explicit per-pin command always wins).
- Runs in the integrated terminal (default, visible/interactive) or a background
  output channel (for non-interactive jobs).

### Scheduling (planned)
- Run a pinned script at a time of day and/or on a repeating interval while VS
  Code is open (in-process timers, not OS cron). The data model already carries
  the schedule fields; the scheduler is a follow-up phase.

### Surfaces
- Activity-bar container with a **Pins** view: **Project Pins** and **Global
  Pins** groups.
- Settings (`saropaWorkspace.*`): `autoPins.patterns`, `doubleClickMs`,
  `defaultUseIntegratedTerminal`, `terminalName`, `interpreterDefaults`.

---

## 3. Scope boundaries

- The extension executes **user-chosen** files locally. It never executes a file
  the user did not pin and run. No telemetry, no network access.
- Phase 1 pins are files. Folder/group entries from imported favorites files are
  skipped until pin groups land.
- Storage is local: a workspace JSON file and extension global state. No external
  service.

---

## 4. Suite integration ("Better Together")

These are candidate integrations, not commitments. Each would be built in the
owning extension's repo, not in the suite wrapper.

- **Workspace + Log Capture** — pin a script that reproduces a bug; a scheduled
  or manual run could tag the resulting Log Capture session with the pin name,
  tying a run to its captured output.
- **Workspace + Lints** — surface the project's lint/analysis entry points as
  auto-pins so a developer can run them in one action.
- **Workspace + Drift Advisor** — pin database seed/migration scripts for
  one-action runs alongside Drift Advisor's profiling.

None of these require the suite wrapper to change beyond adding the extension to
the pack.

---

## 5. Suite manifest change (requires explicit approval — not done here)

To ship Saropa Workspace as part of the suite, the suite's `package.json` would
add the published id to `extensionPack`:

```jsonc
"extensionPack": [
  "saropa.saropa-log-capture",
  "saropa.saropa-lints",
  "saropa.drift-viewer",
  "saropa.saropa-workspace"   // <-- proposed addition
]
```

This is a suite-repo code change and is intentionally **left for the suite
maintainer to apply**. The README member list, the "What's Included" section, and
the architecture diagram would be updated in the same change. This spec does not
modify any suite source.

---

## 6. Verification (for the member extension)

The extension is verified by TypeScript compile (`tsc -p ./ --noEmit`), esbuild
bundle (`npm run build`), and a manual smoke test in the Extension Development
Host. There is no Dart toolchain. Release/packaging uses the extension's own
`scripts/publish.py`.
