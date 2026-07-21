# Milestone 3 - Event to Evidence Extraction

Status: Completed

## Objective

Transform normalized Events into Evidence relationships that can be consumed by future expertise estimation algorithms.

## Architecture

GitHub

↓

Event

↓

Evidence Extractor

↓

Evidence

## Implemented Components

### EvidenceExtractor

Abstract contract for deriving Evidence from Events.

Responsibilities:

* Accept Event objects
* Produce Evidence objects
* Remain independent of estimation logic

### ExpertiseExtractor

First concrete implementation.

Responsibilities:

* Process COMMIT events
* Generate MODIFIED relationships
* Create deterministic Evidence identifiers
* Maintain traceability to source events

## Evidence Model

Evidence consists of:

* id
* source_event_id
* subject_ref
* predicate
* object_ref
* confidence
* metadata

## First Extraction Rule

COMMIT

↓

MODIFIED

For every file touched by a commit:

Developer

↓

MODIFIED

↓

File

## Validation

Validated using live GitHub data from:

facebook/react

Observed pipeline:

GitHub Commit

↓

Event

↓

Evidence

## Outcome

The system now produces explicit relationships between actors and assets.

This marks the transition from data collection to knowledge extraction.

## Next Milestone

Milestone 4 - Evidence to Expertise Estimation
