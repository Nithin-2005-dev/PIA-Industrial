from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.api.services.query_service import QueryService
from app.api.dtos.v1 import ExecutionTraceDTO_v1
from app.kernel.runtime import CognitiveRuntime
from app.core.core_modules import GitHubAdapterFactory
from app.kernel.provider_manager import ProviderManager
from app.kernel.provider import MockLLMProvider

router = APIRouter(prefix="/api/v1/query", tags=["query"])

# Mock dependency injection for now
def get_query_service() -> QueryService:
    return QueryService()

class QueryRequest(BaseModel):
    query: str
    workspace_id: Optional[str] = None
    repository: Optional[str] = None
    repository_session_id: Optional[str] = None

@router.post("", response_model=ExecutionTraceDTO_v1)
async def execute_query(request: QueryRequest, service: QueryService = Depends(get_query_service)):
    # In a real async environment, we might run this in a threadpool
    return service.execute_query(
        request.query,
        workspace_id=request.workspace_id,
        repository=request.repository,
        repository_session_id=request.repository_session_id,
    )
