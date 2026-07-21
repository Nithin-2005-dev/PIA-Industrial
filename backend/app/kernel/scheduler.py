from typing import Any, Callable, Dict, List, Optional
import dataclasses
import time

@dataclasses.dataclass
class Job:
    id: str
    capability_id: str
    arguments: Dict[str, Any]
    priority: int = 50
    dependencies: List[str] = dataclasses.field(default_factory=list)
    status: str = "PENDING"
    result: Optional[Any] = None
    error: Optional[Exception] = None

class Scheduler:
    """
    Decides parallel execution, retries, resource limits, cancellation, and dependency ordering.
    """
    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._running: List[str] = []
        
    def submit(self, job: Job):
        self._jobs[job.id] = job
        
    def get_ready_jobs(self) -> List[Job]:
        """Returns jobs whose dependencies are DONE and are currently PENDING."""
        ready = []
        for job in self._jobs.values():
            if job.status == "PENDING":
                deps_met = all(self._jobs.get(d) and self._jobs[d].status == "DONE" for d in job.dependencies)
                if deps_met:
                    ready.append(job)
        # Sort by priority (higher number = higher priority)
        ready.sort(key=lambda j: j.priority, reverse=True)
        return ready

    def mark_running(self, job_id: str):
        if job_id in self._jobs:
            self._jobs[job_id].status = "RUNNING"
            self._running.append(job_id)

    def mark_done(self, job_id: str, result: Any):
        if job_id in self._jobs:
            self._jobs[job_id].status = "DONE"
            self._jobs[job_id].result = result
            if job_id in self._running:
                self._running.remove(job_id)

    def mark_failed(self, job_id: str, error: Exception):
        if job_id in self._jobs:
            self._jobs[job_id].status = "FAILED"
            self._jobs[job_id].error = error
            if job_id in self._running:
                self._running.remove(job_id)
