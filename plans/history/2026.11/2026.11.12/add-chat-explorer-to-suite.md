# Add Saropa Chat Explorer to the suite

The Saropa Suite extension pack bundled four members (Log Capture, Lints, Drift
Advisor, Workspace). This change adds Saropa Chat Explorer
(`saropa.claude-chat-explorer`), full-text search and resume of Claude Code
session history, as the fifth member. The request is in
`PLAN_integrate_chat_explorer.md` (same folder).

## Finish Report (2026-11-12)

### Scope

Docs and manifest only. The suite is an extension pack; the member extension
lives in its own repo and was not modified.

### Changes

- **`package.json`** — appended `saropa.claude-chat-explorer` to `extensionPack`
  (last; others not reordered). Description names Chat Explorer; added `claude`,
  `claude-code`, `session-history` keywords; version 1.0.8 to 1.0.9.
- **`README.md`** — intro count four to five (and the capability list); new
  "Saropa Chat Explorer" entry under "What's Included"; a "Chat Explorer + the
  suite" Better Together bullet; a Chat Explorer box beside Workspace in the
  architecture diagram; "All five" in Getting Started.
- **`images/icon_saropa_chat_explorer.png`** — member icon resized to 256px.
- **`CHANGELOG.md`** — 1.0.9 section.

### Accuracy note

The Better Together bullet describes what Chat Explorer does on its own (search
and resume sessions); no cross-extension API is claimed.

### Verification

- `package.json` parses as valid JSON.
- The README icon reference resolves to the copied asset.
- No test suite exists in this repo; the extension is not packaged or published
  here.
