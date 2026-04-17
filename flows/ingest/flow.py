"""
Branch-Aware Scheduled Ingest
-----------------------------
Demonstrates @project_schedule: production runs on a weekday cron,
staging runs daily, and feature branches get no schedule at all.

Without @project_schedule you'd have two choices:
  1. @schedule(cron="...") on every branch (wasteful -- feature branches
     run crons nobody asked for)
  2. obproject_deploy.toml branch filtering (all-or-nothing -- the flow
     either deploys or doesn't, so you can't manually trigger it on
     feature branches)

@project_schedule gives you the middle ground: every branch can still
deploy the flow (so you can trigger it manually or via events), but
only the branches you specify get a CronWorkflow.
"""

from metaflow import step, current
from obproject import ProjectFlow, project_schedule


@project_schedule({
    "main": {"cron": "0 8 * * 1-5", "timezone": "America/New_York"},
    "staging": {"daily": True},
})
class IngestFlow(ProjectFlow):

    @step
    def start(self):
        print(f"Branch: {current.branch_name}")
        self.record_count = 42
        self.next(self.end)

    @step
    def end(self):
        print(f"Ingested {self.record_count} records.")
        self.prj.safe_publish_event(
            "ingest_complete", payload={"record_count": self.record_count}
        )


if __name__ == "__main__":
    IngestFlow()
