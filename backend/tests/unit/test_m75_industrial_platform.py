"""M75 real-platform tests for workspace-scoped industrial ingestion."""
from pathlib import Path

from app.industrial.workspace_runtime import IndustrialWorkspaceRuntime


def test_empty_workspace_then_unseen_asset_ingestion_persists(tmp_path: Path):
    runtime = IndustrialWorkspaceRuntime(data_root=tmp_path)
    workspace = runtime.create_workspace("M75 Empty Workspace", workspace_id="m75-empty")

    assert runtime.workspace_summary(workspace.id)["document_count"] == 0
    assert runtime.list_assets(workspace.id) == []
    assert runtime.graph_payload(workspace.id)["total_nodes"] == 0

    inspection = tmp_path / "IR-500_inspection.txt"
    inspection.write_text(
        "Inspection report IR-500 for Pump P-500. Elevated vibration measured 6.4 mm/s. "
        "Technician recommends inspecting Bearing B-12.",
        encoding="utf-8",
    )
    work_order = tmp_path / "WO-500_repair.txt"
    work_order.write_text(
        "Work order WO-500 applies to Process Pump P-500. Replace bearing and align shaft. "
        "Status DEFERRED pending outage window.",
        encoding="utf-8",
    )

    first_job = runtime.ingest_file(workspace.id, inspection)
    second_job = runtime.ingest_file(workspace.id, work_order)

    assert first_job.status == "COMPLETED"
    assert second_job.status == "COMPLETED"
    assert any(asset["asset_id"] == "P-500" for asset in runtime.list_assets(workspace.id))
    assert runtime.graph_payload(workspace.id)["total_nodes"] > 0
    assert runtime.search(workspace.id, "P-500")
    assert "P-500" in runtime.answer_query(workspace.id, "Tell me about P-500")["answer"]

    restarted = IndustrialWorkspaceRuntime(data_root=tmp_path)
    assert any(asset["asset_id"] == "P-500" for asset in restarted.list_assets(workspace.id))
    assert restarted.documents(workspace.id)
    assert restarted.graph_payload(workspace.id)["total_nodes"] > 0


def test_workspace_isolation_for_unseen_assets(tmp_path: Path):
    runtime = IndustrialWorkspaceRuntime(data_root=tmp_path)
    p500 = runtime.create_workspace("P500 Workspace", workspace_id="p500")
    hx204 = runtime.create_workspace("HX204 Workspace", workspace_id="hx204")

    p500_doc = tmp_path / "p500.txt"
    p500_doc.write_text("Inspection IR-500 documents Pump P-500 with abnormal vibration.", encoding="utf-8")
    hx204_doc = tmp_path / "hx204.txt"
    hx204_doc.write_text("Manual for Heat Exchanger HX-204 mentions tube fouling and cleaning.", encoding="utf-8")

    runtime.ingest_file(p500.id, p500_doc)
    runtime.ingest_file(hx204.id, hx204_doc)

    assert any(asset["asset_id"] == "P-500" for asset in runtime.list_assets(p500.id))
    assert not any(asset["asset_id"] == "HX-204" for asset in runtime.list_assets(p500.id))
    assert any(asset["asset_id"] == "HX-204" for asset in runtime.list_assets(hx204.id))
    assert not any(asset["asset_id"] == "P-500" for asset in runtime.list_assets(hx204.id))

