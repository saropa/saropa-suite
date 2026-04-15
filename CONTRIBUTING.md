# Contributing

## Publishing

The publish script validates, packages, and publishes the extension pack to
both the VS Code Marketplace and the Open VSX Registry.

```bash
python scripts/publish.py              # full publish (Marketplace + Open VSX)
python scripts/publish.py --dry-run    # validate + package only, no publish
python scripts/publish.py --skip-ovsx  # skip Open VSX, Marketplace only
```

The version is determined by the first `## [x.y.z]` heading in `CHANGELOG.md`.
If `package.json` has a different version, it is updated automatically.

The script handles everything automatically:

- Reads the version from `CHANGELOG.md` and syncs `package.json`
- Installs/updates `vsce` and `ovsx` CLI tools
- Runs 15+ pre-flight checks (required fields, icon PNG validation, extension IDs, Marketplace listings, git state, etc.)
- Packages the `.vsix` and asks for confirmation before publishing
- Commits the version sync and creates a `vX.Y.Z` git tag after publish
- Writes a full log to `reports/<yyyymmdd>/<datetime>_publish.log`

## Environment variables

| Variable | Required? | Purpose |
|---|---|---|
| `VSCE_PAT` | If not using `vsce login` | Personal Access Token for the VS Code Marketplace |
| `OVSX_PAT` | For Open VSX publishing | Personal Access Token from https://open-vsx.org/ |
| `NO_COLOR` | Optional | Disable colored terminal output |

## Requirements

- Python 3.10+
- Node.js
- npm
