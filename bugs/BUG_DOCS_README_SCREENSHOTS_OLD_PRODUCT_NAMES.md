# BUG: README screenshots show retired product names

**Status: Open**

Created: 2026-11-20
Component: Documentation
File: `README.md` (Saropa Workspace and Saropa Chats sections), `images/screenshots/workspace_sidebar_schedule.png`, `images/screenshots/chats_session_manager_and_activity.png`
Severity: Low

---

## Summary

Two screenshots added to the README on 2026-11-20 were copied from the member projects before they were retaken after the renames. They show names the suite README no longer uses: "Saropa Chat Explorer", "Saropa Log Capture" and "Saropa Drift Advisor" (now "Saropa Chats", "Saropa Capture" and "Saropa Drift"). A reader sees one name in the text and another in the picture.

---

## Attribution Evidence

The images are committed files in this repo, referenced from the suite README, so the defect is in a suite-owned file. The pictures were copied unchanged from the member repos, where the same stale files still exist.

```bash
grep -n "workspace_sidebar_schedule\|chats_session_manager_and_activity" README.md
# README.md: <img src="images/screenshots/workspace_sidebar_schedule.png" ...>
# README.md: <img src="images/screenshots/chats_session_manager_and_activity.png" ...>
```

**Owned file(s):** `README.md`, `images/screenshots/workspace_sidebar_schedule.png`, `images/screenshots/chats_session_manager_and_activity.png`

---

## Actual Behavior

| Image | Source file | Stale text visible |
|---|---|---|
| `chats_session_manager_and_activity.png` | `D:\src\claude-chat-explorer\images\sidebar_session_manager_and_activity_panel.png` | "Saropa Chat Explorer" in the side bar title and the view title |
| `workspace_sidebar_schedule.png` | `D:\src\saropa_workspace\images\screenshot.png` | "SAROPA LOG CAPTURE" panel tab; "Saropa Drift Advisor: no server found" in the status bar |

The Workspace image also shows file names from the author's `contacts` project (`organize_reports.py`, `setup_arb_translate.py`, and others).

## Expected Behavior

Screenshots in the README show the current names: Saropa Chats, Saropa Capture, Saropa Drift. No private project file names.

---

## Root Cause

The images were copied from the member repos' `images/` folders as they stood. Neither source was retaken after the renames. Chats already tracks its own copy of this problem in `D:\src\claude-chat-explorer\bugs\docs_readme_screenshot_old_name.md`.

## Suggested Fix

1. Retake both screenshots with the renamed extensions installed (Saropa Chats and Saropa Capture, plus the renamed Drift once published), ideally from a neutral demo project for Workspace.
2. Replace the two files in `images/screenshots/` under the same names, so the README needs no edit.
3. Until then, remove the two `<img>` lines from `README.md`.

The new images should come from the member repos' updated files, or be taken here, rather than edited by hand.

## Impact

Cosmetic. Marketplace and GitHub readers see mismatched names. No functional effect.
