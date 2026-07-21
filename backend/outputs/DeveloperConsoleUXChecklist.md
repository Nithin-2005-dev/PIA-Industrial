# Developer Console UX Checklist

This checklist is for manual verification of the Developer Console. It is **informational only** and does not block the Knowledge Graph production gate.

## Navigation Flow
- [ ] Explorers are accessible from the main navigation sidebar.
- [ ] Navigation between different Explorers (e.g., Object Inspector, Explainability View) is smooth and maintains URL state.
- [ ] Breadcrumbs or back buttons work as expected.

## Responsiveness
- [ ] UI layouts scale appropriately on 1080p and 1440p resolutions.
- [ ] Sidebars and property panes can be resized or collapsed without breaking the layout.
- [ ] Loading spinners appear during API latency.

## Cytoscape Interactions (Graph Visualization)
- [ ] Graph nodes can be clicked to reveal properties.
- [ ] Zooming and panning operate smoothly without jank.
- [ ] Edges clearly show directional arrows and relationship labels.
- [ ] Highlighting a node dims unrelated components (focus mode).

## Replay Usability
- [ ] Replay controls (Play, Pause, Step) are clearly visible.
- [ ] Stepping through the replay highlights the specific nodes/edges being added or mutated.
- [ ] The replay progress bar matches the actual synchronization state.

## Object Inspector Usability
- [ ] JSON payload view is formatted and syntax-highlighted.
- [ ] Object IDs are clearly visible.
- [ ] Copy-to-clipboard functionality works for Object IDs and JSON payloads.
- [ ] Validation scores and badges reflect real data with clear color coding (Green/Red).

## Explorer Discoverability
- [ ] Search bar is prominent and supports partial matching.
- [ ] Filters (by Type, by Status) are easy to apply and reset.
- [ ] Empty states provide clear calls-to-action (e.g., "No objects found. Try syncing a repository first.").
