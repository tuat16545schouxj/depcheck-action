# Dashboard Reporter

The `dashboard` reporter generates a **self-contained HTML file** that provides a visual overview of dependency health across all detected ecosystems.

## Output

A single `.html` file that can be opened in any browser — no external assets required.

## Features

- Per-ecosystem summary table (total vs. outdated)
- Colour-coded health score (green / amber / red)
- Inline JSON data exposed for custom scripting
- Zero runtime dependencies

## Usage

### CLI (planned)

```bash
depcheck --reporter dashboard --output dashboard.html
```

### Python API

```python
from src.reporters.dashboard_reporter import DashboardReporter
from src.detectors.registry import detect_all

results = detect_all(".")
html = DashboardReporter().render(results)

with open("dashboard.html", "w") as fh:
    fh.write(html)
```

## Score colours

| Score | Colour | Meaning |
|-------|--------|---------|
| ≥ 90% | 🟢 Green | Healthy |
| 70–89% | 🟡 Amber | Needs attention |
| < 70% | 🔴 Red | Critical |

## GitHub Actions example

```yaml
- name: Generate dependency dashboard
  uses: ./
  with:
    reporter: dashboard
    output_path: reports/dashboard.html

- name: Upload dashboard artifact
  uses: actions/upload-artifact@v4
  with:
    name: dependency-dashboard
    path: reports/dashboard.html
```
