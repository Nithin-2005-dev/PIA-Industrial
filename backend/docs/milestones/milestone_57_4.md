# Milestone 57.4: Repository Session & Context Resolution

## Architecture
Introduces the `RepositorySession` to encapsulate all active metadata (branch, commits, timestamps).

## Execution Diagram
`CognitiveSession` -> holds `RepositorySession` -> injected by `ContextBuilder` into `PromptContext`.

## Limitations
Requires valid GitHub tokens for live repositories; fallback relies on cached snapshots.

## Future Extensions
M60 will expand this to support multi-repository diffing by loading multiple sessions simultaneously.
