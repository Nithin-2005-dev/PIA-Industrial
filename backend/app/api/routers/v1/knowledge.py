from fastapi import APIRouter
from app.infrastructure.database.sqlite_provider import get_provider
from app.infrastructure.database.models import EvidenceRecord
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])

class KnowledgeItemDTO(BaseModel):
    id: str
    evidence_type: str
    summary: str
    confidence: float
    subject_id: str
    subject_type: str
    measurement_ids: List[str]

class KnowledgeResponseDTO(BaseModel):
    knowledge: List[KnowledgeItemDTO]

@router.get("/latest", response_model=KnowledgeResponseDTO)
async def get_latest_knowledge():
    provider = get_provider()
    evidence = provider.query(EvidenceRecord, limit=1000)
    result = []
    for e in evidence:
        result.append(KnowledgeItemDTO(
            id=e.identity.object_id,
            evidence_type=e.evidence_type,
            summary=e.summary,
            confidence=e.confidence,
            subject_id=e.subject_id,
            subject_type=e.subject_type,
            measurement_ids=e.measurement_ids
        ))
    return KnowledgeResponseDTO(knowledge=result)

@router.get("/{version_id}", response_model=KnowledgeResponseDTO)
async def get_version_knowledge(version_id: str):
    provider = get_provider()
    evidence = provider.query(EvidenceRecord, limit=1000)
    result = []
    for e in evidence:
        result.append(KnowledgeItemDTO(
            id=e.identity.object_id,
            evidence_type=e.evidence_type,
            summary=e.summary,
            confidence=e.confidence,
            subject_id=e.subject_id,
            subject_type=e.subject_type,
            measurement_ids=e.measurement_ids
        ))
    return KnowledgeResponseDTO(knowledge=result)
