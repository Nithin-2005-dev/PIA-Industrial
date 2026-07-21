# Milestone 42: Durable Platform Storage

M42 adds a durable storage foundation for platform records. It introduces JSONL-backed stores for observations, measurements, evidence, checkpoints, and history snapshots.

## Delivered

- Added `PlatformStorage`, `JsonlRecordStore`, and `StorageSerializer`.
- Added durable append/read/find operations for platform records.
- Added JSON-safe serialization for dataclasses, enums, datetimes, mappings, and sequences.
- Added typed convenience methods for observations, measurements, evidence, checkpoints, and history.
- Registered `PlatformStorage` with the Platform Runtime.
- Added `backend/scripts/test_platform_storage.py`.

## Current Scope

This is a local durable storage foundation, not a production database abstraction.

## Known Limitations

- JSONL append-only files only.
- No indexing beyond linear reads.
- No transactions, locking, compaction, or schema migration.
- No object rehydration into full dataclass instances yet.

## Verification

`python backend/scripts/test_platform_storage.py`

