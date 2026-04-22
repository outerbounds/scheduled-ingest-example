# Branch-aware scheduling example

Demonstrates `@project_schedule` — a wrapper around Metaflow's `@schedule` that
applies different cron schedules depending on which branch is deployed, instead
of giving every branch the same schedule.

## The problem

With a plain `@schedule(cron="0 8 * * 1-5")`, every deployed branch gets its
own CronWorkflow. Feature branches run crons nobody asked for, and the only
workaround is `obproject_deploy.toml` branch filtering — but that prevents the
flow from deploying at all, so you lose the ability to trigger it manually.

## The solution

```python
@project_schedule({
    "main":    {"cron": "0 8 * * 1-5", "timezone": "America/New_York"},
    "staging": {"daily": True},
})
class IngestFlow(ProjectFlow):
    ...
```

| Branch | Behavior |
|--------|----------|
| `main` | Runs weekdays at 8 AM ET via CronWorkflow |
| `staging` | Runs daily via CronWorkflow |
| Any other branch | Flow deploys (can be triggered manually) but no CronWorkflow is created |

## Running locally

```bash
# From this directory:
cd flows/ingest
python flow.py run
```

Since there's no `project_spec` in local runs, `@project_schedule` is a no-op
and the flow runs like any other flow.
