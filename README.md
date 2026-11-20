# Saropa Suite

One-click install for the full Saropa developer toolkit. **Saropa Suite** bundles five powerful VS Code extensions to fortify your Flutter and Dart development workflow, providing persistent capture of debug output, strict behavioral analysis, comprehensive local database diagnostics, a fast project-aware launcher for your files and scripts, and full-text search of your Claude Code session history.

---

## ⚡ Suite Integrations: Better Together

Installing the full Saropa Suite unlocks native, cross-extension APIs that dramatically speed up your workflow:

* **Capture + Lints:** Exported bug reports become actually useful. Saropa Capture natively cross-references runtime errors with static analysis findings. It embeds lint violations (filtered by impact), OWASP executive summaries, and overall project health scores directly into your logs. Stale lint data is automatically refreshed before report generation.
* **Capture + Drift:** Your debugging sessions now carry deep database context. Session metadata bundles query performance stats, schema summaries, anomaly counts, and index suggestions. Right-click any SQL line in your logs to instantly "Open in Saropa Drift" to profile and optimize the query. Root-cause log hints will actively reference Drift database issues.
* **Workspace + the suite:** Pin the rest of the toolkit's entry points as one-click favorites — run a Lints analysis, launch a Saropa Capture repro script, or kick off a Saropa Drift seed/migration — so the tools you installed together are always one action away, from a single sidebar. Saropa Capture also exposes a signal-delta API: bracket a command run with two log markers and ask what errors, warnings, or performance signals changed in between.
* **Chats + the suite:** Find the Claude Code session that worked on your project. Search your session history by word, file, command, branch or PR, see which session edited a file, and resume it from the sidebar.

```
┌─────────────────────────┐         ┌─────────────────────────┐
│     Saropa Workspace    │         │       Saropa Chats      │
│  Pin & run files,       │         │  Search & resume Claude │
│  scripts, entry points  │         │  Code session history   │
└────────────┬────────────┘         └────────────┬────────────┘
             │  Launches                         │  Session search
             └─────────────────┬─────────────────┘
                               ▼
                     ┌───────────────────┐
                     │   SAROPA  SUITE   │
                     └─────────┬─────────┘
               ┌───────────────┴───────────────┐
               │                               │
  ┌────────────┴─────────────┐   ┌─────────────┴────────────┐
  │       Saropa Lints       │   │       Saropa Drift       │
  │                          │   │                          │
  │  Static Behavioral &     │   │  Local DB Analysis &     │
  │  Security Analysis       │   │  Query Profiling         │
  └────────────┬─────────────┘   └─────────────┬────────────┘
               │                               │
               │  Injects OWASP summaries,     │  Syncs SQL stats
               │  health scores, and lint      │  context.
               │  violations.                  │
               │                               │
  ┌────────────┴───────────────────────────────┴─────────────┐
  │                     Saropa Capture                       │
  │         Persistent Runtime Logging & Navigation          │
  └──────────────────────────┬───────────────────────────────┘
                             │
                             │  Generates
                             │
                  ┌──────────┴──────────────────────────┐
                  │  Context-Rich Exported Bug Reports  │
                  └─────────────────────────────────────┘
```

---

## 🛠️ What's Included

### <img src="images/icon_saropa_log_capture.png" width="28" align="top"> [Saropa Capture](https://marketplace.visualstudio.com/items?itemName=saropa.saropa-capture)
**Persistent debug logging.** Saves every debug session to searchable log files instead of losing the Debug Console when you stop. Works with any debug adapter, with a fast log viewer, error classification, Crashlytics and Vitals, SQL diagnostics, session comparison and replay, and rich exports. [Full README](https://github.com/saropa/saropa-log-capture/blob/main/README.md)

<img src="images/screenshots/20260414_project_log_view.png" alt="Log viewer with colored severity markers" width="450">

### <img src="images/icon_saropa_lints.png" width="28" align="top"> [Saropa Lints](https://marketplace.visualstudio.com/items?itemName=saropa.saropa-lints)
**Strict behavioral analysis for Dart and Flutter.** 2,300+ lint rules and quick fixes that catch runtime errors, memory leaks and security issues standard linters miss: OWASP-mapped security rules, library-specific audits, a tiered adoption system, Package Vibrancy dependency scoring, and a VS Code health dashboard. [Full README](https://github.com/saropa/saropa_lints/blob/main/README.md)

<img src="images/screenshots/20260401_problems_tab.png" alt="Flutter memory leak detection in VS Code" width="450">

### <img src="images/icon_saropa_drift_advisor.png" width="28" align="top"> [Saropa Drift](https://marketplace.visualstudio.com/items?itemName=saropa.drift-viewer)
**SQLite/Drift debugging.** A lightweight in-app server paired with a browser UI and a VS Code extension: data browsing, a SQL console and notebook, schema and ER diagrams, data-quality and anomaly checks, snapshots and time travel, and query performance profiling. [Full README](https://github.com/saropa/saropa_drift_advisor/blob/main/README.md)

<img src="images/screenshots/health.png" alt="Database health check scanning tables" width="450">

### <img src="images/icon_saropa_workspace.png" width="28" align="top"> [Saropa Workspace](https://marketplace.visualstudio.com/items?itemName=saropa.saropa-workspace)
**Project-aware launcher.** Pin any file or script as a favorite (single-click opens, double-click runs), with project and global scopes, scheduling, auto-detected recipes, plus a Release Board and HubGrid for work items and GitHub issues. [Full README](https://github.com/saropa/saropa_workspace/blob/main/README.md)

### <img src="images/icon_saropa_chat_explorer.png" width="28" align="top"> [Saropa Chats](https://marketplace.visualstudio.com/items?itemName=saropa.claude-chat-explorer)
**Search and resume Claude Code sessions.** Full-text search of your session history, which session edited a file, git state per session, live status and context warnings, an Activity diagram, and Account & Usage. Indexed locally. [Full README](https://github.com/saropa/claude-chat-explorer/blob/main/README.md)

---

## 📦 Foundation Library: Saropa Dart Utils

### [Saropa Dart Utils](https://pub.dev/packages/saropa_dart_utils)
**280+ production-hardened extension methods** extracted from real Flutter apps — null-safe accessors, parsing/validation helpers, collection and date utilities, with edge cases (empty, null, Unicode, extremes) already handled.

A pure Dart **library**, not a VS Code extension, so it is not bundled in the install. It is the suite's remediation layer: the safe primitives the other tools' fixes steer you toward, plus a `suggest_saropa_utils` scanner that finds hand-rolled code the library already solves. [Full README](https://github.com/saropa/saropa_dart_utils/blob/main/README.md)

---

## 🚀 Getting Started

1. Install **Saropa Suite** from the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=saropa.saropa-suite).
2. All five extensions are installed and activated automatically.
3. No configuration required — each extension works out of the box.

---

## 💬 Contact & License

**Email:** [saropa.suite@saropa.com](mailto:saropa.suite@saropa.com)  
**License:** [MIT](LICENSE)