# Prometheus Reporter

The **Prometheus reporter** renders dependency audit results in the
[Prometheus exposition format](https://prometheus.io/docs/instrumenting/exposition_formats/)
(plain-text, `text/plain; version=0.0.4`).

This allows you to push metrics to a **Prometheus Pushgateway**, scrape them
from a local endpoint, or pipe them into any OpenMetrics-compatible collector.

## Metrics exposed

| Metric | Type | Description |
|--------|------|-------------|
| `depcheck_dependencies_total` | gauge | Total dependencies found across all manifests |
| `depcheck_outdated_total` | gauge | Total outdated dependencies across all manifests |
| `depcheck_dependencies_by_ecosystem` | gauge | Per-manifest dependency count (labels: `ecosystem`, `manifest`) |
| `depcheck_outdated_by_ecosystem` | gauge | Per-manifest outdated count (labels: `ecosystem`, `manifest`) |

## Labels

`depcheck_dependencies_by_ecosystem` and `depcheck_outdated_by_ecosystem` carry
two labels:

- **`ecosystem`** — e.g. `python`, `node`, `rust`
- **`manifest`** — relative path to the manifest file, e.g. `requirements.txt`

## Usage

```yaml
# .github/workflows/depcheck.yml
- uses: your-org/depcheck-action@v1
  with:
    reporter: prometheus
    output_file: metrics.prom
```

### Push to a Pushgateway

```bash
curl --data-binary @metrics.prom \
     http://pushgateway:9091/metrics/job/depcheck/instance/my-repo
```

## Example output

```
# HELP depcheck_dependencies_total Total number of dependencies detected across all ecosystems.
# TYPE depcheck_dependencies_total gauge
depcheck_dependencies_total 42 1700000000000
# HELP depcheck_outdated_total Total number of outdated dependencies detected across all ecosystems.
# TYPE depcheck_outdated_total gauge
depcheck_outdated_total 7 1700000000000
# HELP depcheck_dependencies_by_ecosystem Number of dependencies per ecosystem manifest.
# TYPE depcheck_dependencies_by_ecosystem gauge
depcheck_dependencies_by_ecosystem{ecosystem="python",manifest="requirements.txt"} 30 1700000000000
depcheck_dependencies_by_ecosystem{ecosystem="node",manifest="package.json"} 12 1700000000000
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `timestamp` | `true` | Append Unix-millisecond timestamp to each sample |

Set `timestamp: false` when scraping via a pull-model endpoint (Prometheus
will add its own scrape timestamp).
