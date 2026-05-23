# InfluxDB Reporter

The **InfluxDB reporter** emits dependency audit results as [InfluxDB line-protocol](https://docs.influxdata.com/influxdb/v2/reference/syntax/line-protocol/) metrics, making it easy to track dependency health over time in any InfluxDB-compatible time-series database (InfluxDB v2, Telegraf, etc.).

## Metric shape

Each `DetectionResult` (one per ecosystem / manifest file) produces a single line:

```
depcheck,ecosystem=<name> total=<n>i,outdated=<n>i,up_to_date=<n>i <unix-ns>
```

### Tags

| Tag         | Description                                  |
|-------------|----------------------------------------------|
| `ecosystem` | Language / package manager (e.g. `python`)   |

### Fields

| Field        | Type    | Description                          |
|--------------|---------|--------------------------------------|
| `total`      | integer | Total dependencies detected          |
| `outdated`   | integer | Dependencies with a newer version    |
| `up_to_date` | integer | Dependencies already at latest       |

## Usage

```python
from src.reporters.influxdb_reporter import InfluxDBReporter

# Render only (no HTTP)
reporter = InfluxDBReporter()
print(reporter.render(results))

# Render and push to InfluxDB v2
reporter = InfluxDBReporter(
    url="https://us-east-1-1.aws.cloud2.influxdata.com",
    token="my-api-token",
    org="my-org",
    bucket="depcheck",
)
reporter.render(results)
```

## Configuration

| Parameter   | Default     | Description                                      |
|-------------|-------------|--------------------------------------------------|
| `url`       | `None`      | InfluxDB base URL; omit to skip HTTP write       |
| `token`     | `None`      | InfluxDB API token                               |
| `org`       | `"default"` | InfluxDB organisation                            |
| `bucket`    | `"depcheck"`| Destination bucket                               |
| `timestamp` | current ns  | Override nanosecond timestamp (useful in tests)  |

## Reporter registry key

```
influxdb
```

Example via the registry:

```python
from src.reporters.reporter_registry import get_reporter
reporter = get_reporter("influxdb", url="http://localhost:8086", token="tok")
```
