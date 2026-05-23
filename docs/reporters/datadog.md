# Datadog Reporter

The **Datadog reporter** emits dependency health metrics to the
[Datadog Metrics API](https://docs.datadoghq.com/api/latest/metrics/) as
`gauge` series, one set per ecosystem detected in the repository.

## Metrics emitted

| Metric | Type | Description |
|---|---|---|
| `depcheck.total` | gauge | Total number of dependencies detected |
| `depcheck.outdated` | gauge | Number of outdated dependencies |
| `depcheck.outdated_pct` | gauge | Percentage of outdated dependencies (omitted when total = 0) |

All metrics carry an `ecosystem:<name>` tag so you can filter and group in
Dashboards or Monitors.

## Configuration

| Parameter | Environment variable | Default | Description |
|---|---|---|---|
| `api_key` | `DD_API_KEY` | `None` | Datadog API key – required to POST |
| `app_key` | `DD_APP_KEY` | `None` | Datadog Application key (optional) |
| `host` | `DD_HOST` | `depcheck-action` | Host tag attached to every metric |
| `post` | – | `True` | Set `False` to skip HTTP POST (dry-run / testing) |

## Usage in action.yml

```yaml
- uses: your-org/depcheck-action@v1
  with:
    reporters: datadog
  env:
    DD_API_KEY: ${{ secrets.DD_API_KEY }}
```

## Output format

The reporter also returns the JSON payload as a string, which is written to
`depcheck-datadog.json` in the workspace when running as a GitHub Action.

```json
{
  "series": [
    {
      "metric": "depcheck.total",
      "type": "gauge",
      "points": [[1700000000, 42]],
      "host": "depcheck-action",
      "tags": ["ecosystem:python"]
    }
  ]
}
```

## Datadog Monitor example

Create a monitor on `depcheck.outdated_pct` with threshold `> 20` to get
alerted when more than 20 % of your dependencies are outdated.
