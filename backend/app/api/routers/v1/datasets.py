from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.api.services.dataset_service import DatasetService

router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])

def get_dataset_service() -> DatasetService:
    return DatasetService()

class DatasetActionRequest(BaseModel):
    dataset_id: str

class DatasetSummaryDTO(BaseModel):
    id: str
    name: str
    status: str

class ActionResponseDTO(BaseModel):
    status: str

@router.get("", response_model=List[DatasetSummaryDTO])
async def list_datasets(service: DatasetService = Depends(get_dataset_service)):
    datasets = service.list_datasets()
    return [DatasetSummaryDTO(id=d.get("id", ""), name=d.get("name", ""), status=d.get("status", "")) for d in datasets]

@router.post("/validate", response_model=ActionResponseDTO)
async def validate_dataset(request: DatasetActionRequest, service: DatasetService = Depends(get_dataset_service)):
    success = service.validate_dataset(request.dataset_id)
    if not success:
        raise HTTPException(status_code=400, detail="Validation failed")
    return ActionResponseDTO(status="validated")

@router.post("/register", response_model=ActionResponseDTO)
async def register_dataset(request: DatasetActionRequest, service: DatasetService = Depends(get_dataset_service)):
    success = service.register_dataset(request.dataset_id)
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed")
    return ActionResponseDTO(status="registered")
