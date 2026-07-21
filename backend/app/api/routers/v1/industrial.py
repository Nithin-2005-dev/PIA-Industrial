"""Workspace-scoped Industrial Intelligence API."""
from __future__ import annotations

import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.industrial.workspace_runtime import get_industrial_runtime

router = APIRouter(prefix="/api/v1/industrial", tags=["Industrial"])


class CreateWorkspaceRequest(BaseModel):
    name: str
    description: str = ""


class QueryRequest(BaseModel):
    query: str
    workspace_id: str | None = None
    asset_id: str | None = None


def _workspace_or_404(workspace_id: str | None) -> str:
    try:
        return get_industrial_runtime().require_workspace(workspace_id).id
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Workspace not found: {workspace_id}") from exc


@router.get("/workspaces")
async def list_workspaces() -> dict[str, Any]:
    return {"workspaces": get_industrial_runtime().list_workspaces()}


@router.post("/workspaces")
async def create_workspace(request: CreateWorkspaceRequest) -> dict[str, Any]:
    workspace = get_industrial_runtime().create_workspace(request.name, request.description)
    return {"workspace": get_industrial_runtime().workspace_summary(workspace.id)}


@router.get("/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str) -> dict[str, Any]:
    _workspace_or_404(workspace_id)
    return {"workspace": get_industrial_runtime().workspace_summary(workspace_id)}


@router.post("/workspaces/{workspace_id}/load-demo")
async def load_demo_dataset(workspace_id: str) -> dict[str, Any]:
    _workspace_or_404(workspace_id)
    return get_industrial_runtime().load_demo_dataset(workspace_id)


@router.post("/workspaces/{workspace_id}/documents")
async def upload_document(workspace_id: str, request: Request) -> dict[str, Any]:
    _workspace_or_404(workspace_id)
    form = await request.form()
    upload = form.get("file")
    if upload is None or not hasattr(upload, "filename"):
        raise HTTPException(status_code=400, detail="Missing multipart file field named 'file'")
    filename = Path(str(upload.filename)).name
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
        content = await upload.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)
    try:
        job = get_industrial_runtime().ingest_file(workspace_id, tmp_path, filename)
    finally:
        tmp_path.unlink(missing_ok=True)
    status_code = 400 if job.status == "FAILED" else 200
    if status_code == 400:
        raise HTTPException(status_code=400, detail=job.error or "Document ingestion failed")
    return {"job": asdict(job)}


@router.get("/workspaces/{workspace_id}/documents")
async def get_workspace_documents(workspace_id: str) -> dict[str, Any]:
    _workspace_or_404(workspace_id)
    return await get_documents(workspace_id)


@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, Any]:
    job = get_industrial_runtime().get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Ingestion job not found")
    return {"job": asdict(job)}


@router.get("/overview")
async def get_overview(workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    runtime = get_industrial_runtime()
    assets = runtime.list_assets(workspace_id)
    documents = runtime.documents(workspace_id)
    feed = []
    assets_at_risk = 0
    open_recommendations = 0
    for asset in assets:
        if asset["risk"] in {"HIGH", "MEDIUM"}:
            assets_at_risk += 1
        if asset["open_findings"]:
            open_recommendations += asset["open_findings"]
            feed.append(
                {
                    "type": "INSUFFICIENT EVIDENCE" if asset["risk"] == "UNKNOWN" else "EVIDENCE",
                    "title": f"{asset['asset_id']} intelligence updated",
                    "asset_id": asset["asset_id"],
                    "description": f"{asset['open_findings']} evidence-backed findings currently available.",
                    "action": "Open Asset 360",
                    "severity": "HIGH" if asset["risk"] == "HIGH" else "MEDIUM",
                }
            )
    return {
        "workspace": runtime.workspace_summary(workspace_id),
        "metrics": {
            "total_assets": len(assets),
            "assets_at_risk": assets_at_risk,
            "critical_assets": len([a for a in assets if a["risk"] == "HIGH"]),
            "open_recommendations": open_recommendations,
            "active_compliance_gaps": len((await get_compliance(workspace_id))["compliance_gaps"]),
            "documents": len(documents),
        },
        "feed": feed,
    }


@router.get("/assets")
async def list_assets(workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    return {"assets": get_industrial_runtime().list_assets(workspace_id)}


@router.get("/assets/{asset_id}")
async def get_asset(asset_id: str, workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    services = get_industrial_runtime().services(workspace_id)
    profile = services.asset_service.get_asset_profile(asset_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    maint_intel = services.maintenance_service.analyze_asset(asset_id)
    comp_pkg = services.compliance_service.evaluate_compliance(asset_id)
    exp_pkg = services.expertise_service.evaluate_expertise(asset_id)
    findings = len(maint_intel.get("findings", ())) + len(maint_intel.get("deferred_recommendations", ()))
    failures = len(maint_intel.get("repeated_failures", ()))
    risk = "HIGH" if failures else "MEDIUM" if findings else "UNKNOWN"
    return {
        "profile": {
            "asset_id": profile.asset_id,
            "name": profile.name,
            "asset_type": profile.asset_type,
            "operational_status": "INSUFFICIENT EVIDENCE" if risk == "UNKNOWN" else "EVIDENCE AVAILABLE",
            "risk": risk,
            "confidence": 0.87,
            "manufacturer": profile.manufacturer or "Unknown",
            "model": profile.model or "Unknown",
            "open_recommendations": [r.description for r in maint_intel.get("deferred_recommendations", ())],
        },
        "timeline": [
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "date": event.date.isoformat(),
                "description": event.description,
                "source_document_id": event.source_document_id,
            }
            for event in profile.timeline
        ],
        "compliance": {
            "compliant": comp_pkg.compliant,
            "gaps": [
                {
                    "requirement_id": gap.requirement_id,
                    "status": gap.status,
                    "days_overdue": gap.days_overdue,
                    "severity": gap.severity,
                }
                for gap in comp_pkg.gaps
            ],
        },
        "expertise": {
            "expert_count": exp_pkg.expert_count,
            "top_expert_id": exp_pkg.top_expert_id,
            "concentration_score": exp_pkg.concentration_score,
            "risk_level": exp_pkg.risk_level,
            "recommendation": exp_pkg.recommendation,
        },
        "maintenance_patterns": [
            {"failure_mode": pattern.failure_mode, "occurrences": pattern.occurrences, "confidence": pattern.confidence}
            for pattern in maint_intel.get("repeated_failures", ())
        ],
        "precursors": [
            {"precursor": precursor.precursor_events, "target_failure": precursor.target_failure_mode}
            for precursor in maint_intel.get("failure_precursors", ())
        ],
    }


@router.post("/assets/{asset_id}/rca")
async def trigger_rca(asset_id: str, state: dict[str, float] | None = None, workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    services = get_industrial_runtime().services(workspace_id)
    profile = services.asset_service.get_asset_profile(asset_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not profile.timeline and not state:
        return {"asset_id": asset_id, "root_causes": [], "recommendations": ["NO SUPPORTED CAUSAL HYPOTHESIS"]}
    rca_state = state or {"equipment_failure": 1.0}
    rca_context = services.rca_service.run_rca(rca_state)
    causes = [
        {
            "hypothesis_id": root.id,
            "target": root.subject,
            "score": root.confidence.value if hasattr(root.confidence, "value") else 0.0,
            "is_supported": bool(root.evidence),
            "evidence_count": len(root.evidence),
            "evidence": [{"type": "SUPPORTING", "description": evidence.summary} for evidence in root.evidence],
        }
        for root in rca_context.root_causes
    ]
    return {
        "asset_id": asset_id,
        "root_causes": causes,
        "recommendations": ["NO SUPPORTED CAUSAL HYPOTHESIS"] if not causes else ["Review cited evidence before intervention"],
    }


@router.post("/assets/{asset_id}/simulation")
async def run_simulation(asset_id: str, delay_days: int = 30, workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    services = get_industrial_runtime().services(workspace_id)
    profile = services.asset_service.get_asset_profile(asset_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not profile.timeline:
        return {"asset_id": asset_id, "status": "INSUFFICIENT EVIDENCE", "message": "Counterfactual unavailable without asset history."}
    from app.intelligence.legacy.industrial_simulation import CounterfactualMaintenanceEngine

    return CounterfactualMaintenanceEngine().simulate_delay(profile, delay_days)


@router.get("/decisions")
async def get_decisions(workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    assets = [asset["asset_id"] for asset in get_industrial_runtime().list_assets(workspace_id)]
    if not assets:
        return {"portfolio_id": "empty", "total_estimated_cost": 0, "overall_risk_reduction": 0, "interventions": []}
    portfolio = get_industrial_runtime().services(workspace_id).decision_service.generate_portfolio(assets)
    return {
        "portfolio_id": portfolio.portfolio_id,
        "total_estimated_cost": portfolio.total_estimated_cost,
        "overall_risk_reduction": portfolio.overall_risk_reduction,
        "interventions": [
            {
                "intervention_id": item.intervention_id,
                "asset_id": item.asset_id,
                "action_type": item.action_type,
                "title": item.title,
                "description": item.description,
                "estimated_cost": item.estimated_cost,
                "risk_reduction_score": item.risk_reduction_score,
                "compliance_impact": item.compliance_impact,
            }
            for item in portfolio.interventions
        ],
    }


@router.get("/graph")
async def get_industrial_graph(workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    return get_industrial_runtime().graph_payload(workspace_id)


@router.get("/documents")
async def get_documents(workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    documents = []
    for document in get_industrial_runtime().documents(workspace_id):
        documents.append(
            {
                "document_id": document["document_id"],
                "name": document["name"],
                "type": document["type"],
                "status": document["status"],
                "timestamp": document["timestamp"],
                "extracted_entities": [e["value"] for e in document.get("entities", []) if e["type"] == "equipment_tag"],
                "evidence_count": len(document.get("chunks", [])),
                "stages": document.get("stages", []),
                "entity_summary": document.get("entity_summary", {}),
            }
        )
    return {"documents": documents}


@router.get("/maintenance")
async def get_maintenance(workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    services = get_industrial_runtime().services(workspace_id)
    deferred = []
    for asset in get_industrial_runtime().list_assets(workspace_id):
        intel = services.maintenance_service.analyze_asset(asset["asset_id"])
        for rec in intel.get("deferred_recommendations", ()):
            deferred.append(
                {
                    "asset_id": asset["asset_id"],
                    "recommendation": rec.description,
                    "reason": "Derived from unresolved inspection evidence",
                    "priority": rec.severity,
                    "status": "DEFERRED",
                    "timestamp": rec.recommended_date.isoformat(),
                    "source_document_id": rec.source_document_id,
                }
            )
    return {"deferred_recommendations": deferred}


@router.get("/failures")
async def get_failures(workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    services = get_industrial_runtime().services(workspace_id)
    patterns = []
    for asset in get_industrial_runtime().list_assets(workspace_id):
        intel = services.maintenance_service.analyze_asset(asset["asset_id"])
        for failure in intel.get("repeated_failures", ()):
            patterns.append(
                {
                    "asset_id": asset["asset_id"],
                    "pattern": failure.failure_mode,
                    "occurrences": failure.occurrences,
                    "confidence": failure.confidence,
                    "potential_precursors": [],
                    "source_documents": failure.source_documents,
                }
            )
    return {"recurring_failures": patterns}


@router.get("/compliance")
async def get_compliance(workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    services = get_industrial_runtime().services(workspace_id)
    gaps = []
    for asset in get_industrial_runtime().list_assets(workspace_id):
        package = services.compliance_service.evaluate_compliance(asset["asset_id"])
        for gap in package.gaps:
            gaps.append(
                {
                    "asset_id": asset["asset_id"],
                    "requirement": gap.requirement_id,
                    "status": gap.status,
                    "reason": f"{gap.days_overdue} days overdue" if gap.days_overdue else "Review required",
                    "severity": gap.severity,
                }
            )
    return {"compliance_gaps": gaps}


@router.get("/search")
async def search(query: str, workspace_id: str | None = Query(default=None)) -> dict[str, Any]:
    workspace_id = _workspace_or_404(workspace_id)
    return {"results": get_industrial_runtime().search(workspace_id, query)}


@router.post("/query")
async def industrial_query(request: QueryRequest) -> dict[str, Any]:
    workspace_id = _workspace_or_404(request.workspace_id)
    return get_industrial_runtime().answer_query(workspace_id, request.query)


@router.post("/workspaces/{workspace_id}/reset")
async def reset_workspace(workspace_id: str) -> dict[str, Any]:
    """Reset a workspace to its initial state. Demo workspaces auto-reload."""
    _workspace_or_404(workspace_id)
    return get_industrial_runtime().reset_workspace(workspace_id)

