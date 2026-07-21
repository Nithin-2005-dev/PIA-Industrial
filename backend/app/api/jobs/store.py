import uuid
from typing import Dict, Any, Optional
from datetime import datetime

class JobStore:
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self, job_type: str) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "job_id": job_id,
            "type": job_type,
            "status": "QUEUED",
            "progress": 0,
            "started_at": datetime.now(),
            "metrics": None
        }
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)

    def update_job(self, job_id: str, status: str, progress: int, metrics: Optional[Dict[str, Any]] = None):
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = status
            self._jobs[job_id]["progress"] = progress
            if metrics:
                self._jobs[job_id]["metrics"] = metrics
