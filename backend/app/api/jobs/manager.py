import asyncio
from typing import Callable, Coroutine, Any
from app.api.jobs.store import JobStore

class JobManager:
    def __init__(self, store: JobStore):
        self.store = store

    async def submit_job(self, job_type: str, task_func: Callable[[str], Coroutine[Any, Any, None]]) -> str:
        job_id = self.store.create_job(job_type)
        
        # Fire and forget
        asyncio.create_task(self._run_job(job_id, task_func))
        return job_id

    async def _run_job(self, job_id: str, task_func: Callable[[str], Coroutine[Any, Any, None]]):
        self.store.update_job(job_id, "RUNNING", 10)
        try:
            await task_func(job_id)
        except Exception as e:
            self.store.update_job(job_id, "FAILED", 0, metrics={"error": str(e)})
