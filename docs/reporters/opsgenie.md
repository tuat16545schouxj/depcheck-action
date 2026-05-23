# OpsGenie Reporter

The **OpsGenie reporter** sends a deduplicated alert to [OpsGenie](https://www.atlassian.com/software/opsgenie) for every ecosystem that contains at least one outdated dependency.

## Configuration

| Parameter | Environment variable | Default | Description |
|-----------|----------------------|---------|-------------|
| `api_key` | `OPSGENIE_API_KEY` | — | OpsGenie API key (required) |
| `team` | `OPSGENIE_TEAM` | `None` | Team name to assign as responder |
| `priority` | `OPSGENIE_PRIORITY` | `P3` | Alert priority (`P1`–`P5`) |
| `dry_run` | `OPSGENIE_DRY_RUN` | `false` | Build payloads but skip HTTP calls |

## Alert structure

Each alert is keyed by the **alias** `depcheck-<ecosystem>`, so repeated runs update the same open alert rather than flooding the queue.

```json
{
  "message": "[depcheck] 3 outdated dep(s) in python",
  "alias": "depcheck-python",
  "description": "Outdated packages detected in **python** (requirements.txt):\nrequests, flask, boto3",
  "priority": "P3",
  "tags": ["depcheck", "python"],
  "responders": [{"name": "platform", "type": "team"}]
}
```

## Usage in action.yml

```yaml
- uses: your-org/depcheck-action@v1
  with:
    reporters: opsgenie
    opsgenie_api_key: ${{ secrets.OPSGENIE_API_KEY }}
    opsgenie_team: platform
    opsgenie_priority: P2
```

## Output

`render()` returns a JSON string summarising how many alerts were dispatched:

```json
{"alerts_sent": 2, "dry_run": false}
```

Up-to-date ecosystems are silently skipped — no alert is created or updated for them.
