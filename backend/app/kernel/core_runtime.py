from typing import Any, Dict
from app.kernel.context import ExecutionContext
from app.kernel.scheduler import Job

class KernelRuntime:
    """
    The Execution Runtime from Phase 1 of the Reasoning Operating System architecture.
    """
    def __init__(self, context: ExecutionContext):
        self.context = context
        
    def execute_job(self, job_id: str) -> Any:
        """
        Executes a job using the capability registry and resource manager.
        """
        self.context.scheduler.mark_running(job_id)
        job = self.context.scheduler._jobs[job_id]
        capability = self.context.registry.get(job.capability_id)
        
        if not capability:
            error = ValueError(f"Capability {job.capability_id} not found in registry.")
            self.context.scheduler.mark_failed(job_id, error)
            raise error
            
        try:
            # Phase 1: Dummy execution logic that proves resources can be acquired
            # In real execution, this would call the Capability Executor
            allocation_id = self.context.resources.allocate(None) # type: ignore
            
            # Simulate execution
            result = {"status": "success", "capability": capability.id, "executed": True}
            
            # Release resources
            self.context.resources.release(allocation_id)
            
            self.context.scheduler.mark_done(job_id, result)
            return result
            
        except Exception as e:
            self.context.scheduler.mark_failed(job_id, e)
            raise e
            
    def run_pipeline(self) -> list[Any]:
        """
        Executes all ready jobs from the scheduler in dependency order.
        """
        results = []
        while True:
            ready_jobs = self.context.scheduler.get_ready_jobs()
            if not ready_jobs:
                break
                
            for job in ready_jobs:
                res = self.execute_job(job.id)
                results.append(res)
                
        return results
