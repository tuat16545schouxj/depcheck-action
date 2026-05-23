# Graphite Reporter

The **Graphite reporter** emits dependency audit results as [Graphite plaintext
protocol](https://graphite.readthedocs.io/en/latest/feeding-carbon.html#the-plaintext-protocol)
metrics, making it easy to track dependency health over time in any
time-series stack (Graphite, Grafana, InfluxDB via relay, etc.).

## Metric schema

For every dependency detected the reporter emits:

```
<prefix>.<ecosystem>.<package_name>.outdated <0|1> <unix_timestamp>
```

In addition, two summary gauges are emitted per ecosystem:

```
<prefix>.<ecosystem>.summary.total   <count> <unix_timestamp>
<prefix>.<ecosystem>.summary.outdated <count> <unix_timestamp>
```

### Sanitisation rules

| Character | Replacement |
|-----------|-------------|
| `-`       | `_`         |
| `/`       | `.`         |
| ` `       | `_`         |
| uppercase | lowercased  |

## Configuration

| Parameter   | Type   | Default      | Description                                  |
|-------------|--------|--------------|----------------------------------------------|
| `host`      | str    | `None`       | Graphite host. When set, metrics are pushed. |
| `port`      | int    | `2003`       | Graphite plaintext TCP port.                 |
| `prefix`    | str    | `depcheck`   | Metric path prefix.                          |
| `timestamp` | int    | current time | Unix timestamp (mainly for testing).         |

## Usage

### Print metrics to stdout

```python
from src.reporters.graphite_reporter import GraphiteReporter
from src.detectors.registry import detect_all

results = detect_all(".")
print(GraphiteReporter().render(results))
```

### Push directly to Graphite

```python
reporter = GraphiteReporter(host="graphite.internal", port=2003, prefix="ci.depcheck")
reporter.render(results)  # pushes over TCP and also returns the payload
```

### GitHub Actions step

```yaml
- name: Push dependency metrics to Graphite
  run: |
    python -c "
    from src.reporters.graphite_reporter import GraphiteReporter
    from src.detectors.registry import detect_all
    GraphiteReporter(host='${{ secrets.GRAPHITE_HOST }}').render(detect_all('.'))
    "
```

## Example output

```
depcheck.python.requests.outdated 1 1700000000
depcheck.python.flask.outdated 0 1700000000
depcheck.python.summary.total 2 1700000000
depcheck.python.summary.outdated 1 1700000000
```
