# Saropa Suite

One-click install for the full Saropa developer toolkit.

## Included extensions

| Extension | What it does |
|---|---|
| **[Saropa Log Capture](https://marketplace.visualstudio.com/items?itemName=saropa.saropa-log-capture)** | Automatically saves Debug Console output to persistent, searchable log files. Virtual-scrolling viewer, error intelligence, signals, SQL diagnostics, session comparison, and export. |
| **[Saropa Lints](https://marketplace.visualstudio.com/items?itemName=saropa.saropa-lints)** | 1700+ custom Dart and Flutter lint rules. Catches memory leaks, OWASP-mapped security vulnerabilities, and runtime crashes. AI-ready diagnostics for faster repairs. |
| **[Saropa Drift Advisor](https://marketplace.visualstudio.com/items?itemName=saropa.drift-viewer)** | Schema health, query performance, index suggestions, and anomaly detection for Drift (SQLite) databases. |

## Screenshots

### Saropa Log Capture

![Debug output in the log viewer with colored severity markers, framework classification, and run navigation](assets/screenshots/20260414_project_log_view.png)

![Log viewer showing Drift SQL queries with syntax highlighting and diagnostic badges](assets/screenshots/20260401_log_viewer_sql.png)

### Saropa Lints

![Flutter memory leak detection in VS Code showing undisposed TextEditingController](assets/screenshots/20260401_problems_tab.png)

![AI fixing Flutter security vulnerability automatically](assets/screenshots/20260401_AI_solver_tab.png)

### Saropa Drift Advisor

![Database health check scanning tables for data quality issues like NULLs, duplicates, and outliers](assets/screenshots/health.png)

![Query performance profiler tracking slow queries with execution times and row counts](assets/screenshots/perf.png)

## Why install the pack?

Each extension works well standalone, but they unlock deeper integration when installed together:

- **Log Capture + Lints** — Bug reports include lint violations filtered by impact, OWASP executive summaries, health scores, and one-click "Explain Rule" links. Stale lint data is refreshed automatically before report generation.
- **Log Capture + Drift Advisor** — Session metadata and sidecar files carry query performance stats, schema summaries, anomaly counts, index suggestions, and diagnostic issues. Right-click SQL lines for "Open in Drift Advisor". Root-cause hints reference Drift issues.

## Getting started

1. Install **Saropa Suite** from the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=saropa.saropa-suite).
2. All three extensions are installed and activated automatically.
3. No configuration required — each extension works out of the box.

## Contact

**Email:** [saropa.suite@saropa.com](mailto:saropa.suite@saropa.com)

## License

[MIT](LICENSE)
