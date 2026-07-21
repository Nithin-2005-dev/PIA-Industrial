# M75 Real Platform Flow

PIA Industrial is now structured as an Industrial Knowledge Intelligence Platform demonstrated with P-101, not a P-101-only dashboard.

## Quick Demo

1. Select `P-101 Demo Plant`.
2. Review Overview, Assets, Documents, Knowledge Graph, Maintenance, Failure Intelligence, Compliance, and Decisions.
3. Ask Copilot questions while the P-101 demo workspace is active.

## Real Platform Flow

1. Create a new workspace from the header.
2. Open Documents.
3. Upload supported files: TXT, MD, LOG, CSV, XLSX, XLS, or text-based PDF.
4. Wait for ingestion to complete.
5. Review discovered assets, extracted document evidence, graph nodes and edges, and Copilot answers.

## Synthetic Generalization Dataset

`data/synthetic/hx204/` contains a non-P-101 synthetic dataset:

- `HX-204_equipment_manual.txt`
- `IR-204_inspection_report.txt`
- `WO-204_maintenance_work_order.txt`

Upload these files into a new empty workspace to demonstrate that PIA discovers HX-204 without source-code changes or manual database editing.

## Evidence Rules

- Empty workspaces show empty states, not demo assets.
- Copilot searches only the active workspace.
- Intelligence outputs return insufficient evidence or no supported hypothesis when the workspace lacks required facts.
- P-101 remains a synthetic sample dataset and should not be represented as real plant data.

