from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.api.services.benchmark_service import BenchmarkService
from app.api.jobs.manager import JobManager
from app.api.jobs.store import JobStore

router = APIRouter(prefix="/api/v1/benchmark", tags=["benchmark"])

# In a real app, these would be singletons injected via Depends
_job_store = JobStore()
_job_manager = JobManager(_job_store)
_benchmark_service = BenchmarkService(_job_manager, _job_store)

def get_benchmark_service() -> BenchmarkService:
    return _benchmark_service

class BenchmarkRequest(BaseModel):
    dataset: str

class BenchmarkJobResponse(BaseModel):
    job_id: str
    status: str

class BenchmarkProgressResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    metrics: Optional[dict] = None

class BenchmarkResultResponse(BaseModel):
    metrics: dict

@router.post("", response_model=BenchmarkJobResponse)
async def trigger_benchmark(request: BenchmarkRequest, service: BenchmarkService = Depends(get_benchmark_service)):
    job_id = await service.trigger_benchmark(request.dataset)
    return BenchmarkJobResponse(job_id=job_id, status="QUEUED")

@router.get("/{job_id}/progress", response_model=BenchmarkProgressResponse)
async def get_benchmark_progress(job_id: str, service: BenchmarkService = Depends(get_benchmark_service)):
    job = service.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return BenchmarkProgressResponse(**job)

@router.get("/{job_id}/result", response_model=BenchmarkResultResponse)
async def get_benchmark_result(job_id: str, service: BenchmarkService = Depends(get_benchmark_service)):
    job = service.get_job_status(job_id)
    if not job or job["status"] != "COMPLETED":
        raise HTTPException(status_code=400, detail="Job not completed or not found")
    return BenchmarkResultResponse(metrics=job.get("metrics", {}))
