# Branch-Aware Scheduling

Production ML pipelines need different schedules on different branches — daily in prod, hourly in staging, no schedule on feature branches. Without `@project_schedule`, you're stuck choosing between wasteful per-branch crons or all-or-nothing deploy filtering.

`@project_schedule` gives the middle ground: every branch deploys the flow (so you can trigger manually or via events), but only specified branches get a CronWorkflow.

## Architecture

```
ScheduledIngestFlow
  main:    @schedule(cron="0 8 * * 1-5")  — weekday mornings
  staging: @schedule(daily=True)           — daily
  feature: no schedule, but flow is deployed (manual trigger OK)
```

## Platform features used

- **@project_schedule**: ob-project-utils wrapper around Metaflow's `@schedule` decorator. Adds branch-awareness — different cron per branch, no schedule for unspecified branches. Under the hood, it's a `FlowMutator` that applies the right `@schedule` based on which branch the flow is deployed to.
- **[dev-assets]**: Read production data from main on feature branches
- **Teardown**: CI cleans up Argo resources on branch merge/delete

## Flows

| Flow | Trigger | What it does |
|------|---------|-------------|
| ScheduledIngestFlow | @project_schedule (varies by branch) | Simulated data ingest with branch-specific scheduling |

## CI strategy

Deploy + teardown. All pushes deploy (flow is available on every branch). On PR merge or branch delete, teardown removes the branch's CronWorkflow and resources.

Uses `--from-obproject-toml` for auth.

## Run locally

```bash
python flows/ingest/flow.py run
```

The schedule only applies when deployed to the platform — local runs execute immediately.

## Good to know

- `@project_schedule` maps branch names to schedule configs. Branches not in the map get no CronWorkflow but the flow template is still deployed (can be triggered manually).
- This is different from `obproject_deploy.toml` branch filtering, which prevents the flow from deploying at all.
- The schedule config supports both cron and convenience shortcuts: `{"cron": "0 8 * * 1-5"}`, `{"daily": True}`, `{"hourly": True}`.
