# Badge Reporter

The **badge** reporter produces a [Shields.io endpoint](https://shields.io/endpoint) JSON payload that can be embedded in a README to display live dependency-health status.

## Usage

```yaml
- uses: your-org/depcheck-action@v1
  with:
    reporter: badge
    badge-output: badge.json   # written to repo root by default
```

Then add the badge to your `README.md`:

```markdown
![dependency health](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/your-org/your-repo/main/badge.json)
```

## Output format

```json
{
  "schemaVersion": 1,
  "label": "dependencies",
  "message": "3 outdated",
  "color": "orange",
  "namedLogo": "dependabot"
}
```

## Colour thresholds

| Outdated ratio | Colour |
|---------------|--------|
| 0 % | `brightgreen` |
| 1 – 10 % | `green` |
| 11 – 25 % | `yellow` |
| 26 – 50 % | `orange` |
| > 50 % | `red` |
| No data | `lightgrey` |

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `label` | `dependencies` | Text shown on the left side of the badge |

## Programmatic use

```python
from src.reporters.badge_reporter import BadgeReporter
from src.detectors.registry import detect_all

results = detect_all("/path/to/repo")
reporter = BadgeReporter(label="deps")
print(reporter.render(results))
```
