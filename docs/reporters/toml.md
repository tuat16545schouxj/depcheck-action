# TOML Reporter

The **TOML reporter** serialises dependency-audit results into a structured
[TOML](https://toml.io/) document, making it easy to consume the output from
other TOML-aware tooling or configuration pipelines.

## Usage

```yaml
# .github/workflows/depcheck.yml
- uses: your-org/depcheck-action@v1
  with:
    reporter: toml
    output-file: depcheck-results.toml
```

## Output structure

```toml
[meta]
generated_at = "2024-06-01T12:00:00Z"
total_dependencies = 42
total_outdated = 7

[[ecosystems]]
ecosystem = "python"
manifest  = "requirements.txt"
total     = 10
outdated  = 3

  [[ecosystems.dependencies]]
  name     = "requests"
  current  = "2.28.0"
  latest   = "2.31.0"
  outdated = true

  [[ecosystems.dependencies]]
  name     = "flask"
  current  = "2.3.2"
  latest   = "2.3.2"
  outdated = false
```

## Requirements

| Package | Purpose | Required? |
|---------|---------|----------|
| `tomli_w` | Write TOML (Python < 3.11) | Optional |
| `tomllib` | Built-in TOML parser (Python ≥ 3.11) | Bundled |

Install the optional write dependency:

```bash
pip install tomli_w
```

Without `tomli_w` the reporter falls back to a built-in minimal emitter that
covers all fields produced by depcheck-action.

## Fields

### `[meta]`

| Field | Type | Description |
|-------|------|-------------|
| `generated_at` | string (ISO-8601) | UTC timestamp of report generation |
| `total_dependencies` | integer | Total dependencies across all ecosystems |
| `total_outdated` | integer | Total outdated dependencies |

### `[[ecosystems]]`

| Field | Type | Description |
|-------|------|-------------|
| `ecosystem` | string | Language / package manager name |
| `manifest` | string | Path to the manifest file scanned |
| `total` | integer | Dependencies in this manifest |
| `outdated` | integer | Outdated count for this manifest |

### `[[ecosystems.dependencies]]`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Package name |
| `current` | string | Currently pinned version |
| `latest` | string | Latest available version |
| `outdated` | boolean | Whether an upgrade is available |
