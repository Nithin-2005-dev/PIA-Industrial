from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Callable

from app.core.common import RetryPolicy
from app.core.common import utc_now


@dataclass
class ScheduledJob:
    id: str
    handler: Callable[[], None]
    run_at: datetime
    interval: timedelta | None = None
    cron: str | None = None
    retry_policy: RetryPolicy = RetryPolicy()
    attempts: int = 0
    last_error: str | None = None


class Scheduler:
    def __init__(
        self,
    ):
        self._jobs: dict[str, ScheduledJob] = {}

    def schedule_once(
        self,
        job_id: str,
        handler: Callable[[], None],
        delay: timedelta = timedelta(),
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._jobs[job_id] = ScheduledJob(
            id=job_id,
            handler=handler,
            run_at=utc_now() + delay,
            retry_policy=retry_policy or RetryPolicy(),
        )

    def schedule_periodic(
        self,
        job_id: str,
        handler: Callable[[], None],
        interval: timedelta,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._jobs[job_id] = ScheduledJob(
            id=job_id,
            handler=handler,
            run_at=utc_now() + interval,
            interval=interval,
            retry_policy=retry_policy or RetryPolicy(),
        )

    def schedule_cron(
        self,
        job_id: str,
        handler: Callable[[], None],
        cron: str,
    ) -> None:
        # Cron parsing is intentionally deferred; this stores the stable
        # future-ready contract and makes distributed scheduling pluggable.
        self._jobs[job_id] = ScheduledJob(
            id=job_id,
            handler=handler,
            run_at=utc_now(),
            cron=cron,
        )

    def run_due(
        self,
        now: datetime | None = None,
    ) -> tuple[str, ...]:
        now = now or utc_now()
        executed: list[str] = []
        for job in list(self._jobs.values()):
            if job.run_at > now:
                continue
            try:
                job.retry_policy.run(job.handler)
                job.attempts += 1
                job.last_error = None
                executed.append(job.id)
            except Exception as exc:
                job.last_error = str(exc)
            if job.interval is not None:
                job.run_at = now + job.interval
            elif job.cron is None:
                self._jobs.pop(
                    job.id,
                    None,
                )
        return tuple(executed)

    def jobs(
        self,
    ) -> tuple[ScheduledJob, ...]:
        return tuple(self._jobs.values())

