# M33 Signal Intelligence And Knowledge Base

## Purpose

M33 extends the Measurement Operating System with the knowledge layer needed to
understand arbitrary software signals before they become measurements.

The architecture remains:

```text
Adapters
  -> Observation Layer
  -> Signal Intelligence & Knowledge Base
  -> Measurement Operating System
  -> Evidence Intelligence Platform
  -> Expertise Layer
```

Evidence still receives only validated `Measurement` objects, and Expertise
must consume evidence rather than measurements. M33 improves how raw software
signals are registered, classified, mapped and explained.

## Package Additions

```text
app/measurement/signals.py
  SignalDefinition, SignalRegistry, DefaultSignalCatalog

app/measurement/signal_ontology.py
  SignalOntology, signal relationships and signal domains

app/measurement/signal_classifier.py
  rule, ontology, embedding-similarity and optional LLM classification

app/measurement/mapping.py
  signal-to-measurement mapping registry and resolver

app/measurement/signal_validation.py
  signal definition validation and semantic mapping validation

app/measurement/standards.py
  ISO, CISQ, DORA, SPACE, GQM and GSN metadata

app/measurement/domain_packs.py
  Architecture, Code Quality, Git Analytics and other domain packs

app/measurement/measurement_knowledge.py
  rich scientific and business measurement knowledge entries

app/measurement/benchmark_datasets.py
  benchmark dataset registry and scope metadata

app/measurement/knowledge_api.py
  abstraction-first read API for signals, mappings, standards and benchmarks
```

## Signal Registry

Each signal definition is immutable and versioned.

```text
SignalDefinition
  id
  name
  display_name
  description
  source_adapter
  source_tool
  data_type
  unit
  value_constraints
  expected_range
  semantic_category
  tags
  version
  lifecycle
  provenance
  reliability
  supported_measurement_packs
  validation_rules
```

Plugins can dynamically register new signal definitions without engine changes.

## Signal Ontology

The signal ontology models domains such as:

- source control
- static analysis
- runtime
- build systems
- CI/CD
- cloud
- infrastructure
- security
- testing
- documentation
- databases
- AI systems
- developer collaboration
- project management

Relationships include:

- belongs to
- derived from
- equivalent to
- influences
- conflicts with
- complements
- requires

## Semantic Classification

New signals are classified through a layered strategy:

```text
SoftwareSignal
  -> Rule-Based Classification
  -> Ontology Lookup
  -> Embedding Similarity Boundary
  -> Optional LLM Boundary
  -> Human Approval When Confidence Is Low
```

ML and LLM paths recommend classifications only. Deterministic registry and
ontology rules remain the source of truth.

## Mapping Engine

The mapping engine resolves:

```text
Signal
  -> Measurement Concept
  -> Measurement Definition
  -> Evaluator
  -> Measurement Object
```

Mappings are versioned, explainable and traceable. Supported cardinalities:

- one-to-one
- one-to-many
- many-to-one

## Software Measurement Knowledge Base

`SoftwareMeasurementKnowledgeBase` stores measurement-definition knowledge:

- scientific definition
- business definition
- formula
- dependencies
- required signals
- units
- expected range
- confidence model
- uncertainty model
- validation rules
- normalization strategy
- aggregation strategy
- benchmark strategy
- interpretation guide
- assumptions
- known limitations
- standards references
- research references
- version history

The structure is intentionally registry-like so it can scale to 1000+
measurement definitions.

## Standards Alignment

Standards are metadata, not hardcoded algorithms.

Current catalog entries include:

- ISO/IEC 15939
- ISO/IEC 25010
- ISO/IEC 25023
- CISQ Software Quality Measures
- DORA Metrics
- SPACE Framework
- Goal-Question-Metric
- Goal Structuring Notation

## Benchmarks

`BenchmarkDatasetRegistry` supports benchmark scopes:

- repository
- team
- organization
- programming language
- framework
- repository size
- industry
- open source
- internal enterprise

Measurements can be compared against benchmark distributions without changing
measurement definitions.

## Knowledge API

`MeasurementKnowledgeApi` exposes abstraction-first reads for:

- signal definitions
- measurement definitions
- mappings
- mapping explanations
- ontology relationships
- measurement knowledge entries
- benchmark metadata
- standards references

## Validation

M33 validation is covered by:

```text
backend/scripts/test_measurement_engine.py
```

The script exercises:

- signal registration
- signal value validation
- semantic classification
- signal-to-measurement mapping
- mapping validation
- standards lookup
- domain packs
- measurement knowledge entries
- benchmark datasets
- knowledge API queries
