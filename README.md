# depcheck-action

> GitHub Action that audits outdated dependencies across polyglot repos and opens summarized PRs.

---

## Installation

```bash
pip install depcheck-action
```

Or add it directly to your GitHub Actions workflow — no local installation required.

---

## Usage

Add the following to `.github/workflows/depcheck.yml`:

```yaml
name: Dependency Audit

on:
  schedule:
    - cron: "0 9 * * 1"   # Every Monday at 9am
  workflow_dispatch:

jobs:
  depcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run depcheck-action
        uses: your-org/depcheck-action@v1
        with:
          languages: "python,node,go"
          open_pr: true
          pr_title: "chore: update outdated dependencies"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Inputs

| Input       | Description                                      | Default          |
|-------------|--------------------------------------------------|------------------|
| `languages` | Comma-separated list of ecosystems to audit      | `python,node`    |
| `open_pr`   | Automatically open a summarized PR with findings | `true`           |
| `pr_title`  | Title for the generated pull request             | `chore: depcheck`|

---

## How It Works

1. Scans your repository for dependency manifests (`requirements.txt`, `package.json`, `go.mod`, etc.)
2. Checks each dependency against its upstream registry for newer versions.
3. Opens a single summarized pull request listing all outdated packages with recommended upgrades.

---

## License

[MIT](LICENSE)