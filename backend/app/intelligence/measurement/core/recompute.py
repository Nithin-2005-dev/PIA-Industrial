"""
Architectural Constraint: Recomputes must be append-only. Historical metric rows must not be mutated, only superseded by new logic versions.
"""
from collections import defaultdict


class MeasurementDependencyGraph:

    def __init__(
        self,
    ):
        self._dependents = defaultdict(set)

    def register(
        self,
        measurement_id: str,
        dependencies: tuple[str, ...],
    ):
        for dependency_id in dependencies:
            self._dependents[dependency_id].add(
                measurement_id
            )

    def affected_by(
        self,
        changed_measurement_id: str,
    ) -> set[str]:
        affected = set()
        frontier = [
            changed_measurement_id
        ]

        while frontier:
            current = frontier.pop()

            for dependent in self._dependents.get(
                current,
                set(),
            ):
                if dependent in affected:
                    continue

                affected.add(
                    dependent
                )
                frontier.append(
                    dependent
                )

        return affected


import uuid
import logging
from typing import Any, Optional
from datetime import datetime, UTC
from dataclasses import replace
from app.intelligence.measurement.core.audit import RecomputeAuditRecord

logger = logging.getLogger(__name__)

class AppendOnlyRecomputeEngine:
    def __init__(self, measurement_engine, store, audit_logger, quality_gate):
        self.engine = measurement_engine
        self.store = store
        self.audit = audit_logger
        self.quality = quality_gate

    def recompute_historical_measurement(self, old_measurement: Any, raw_observation: Any, context: Any) -> Optional[Any]:
        """
        Safely re-evaluates a past observation using current logic.
        """
        # 1. Run the new math (The engine now contains our sterilized V2 evaluators)
        new_measurements = self.engine.measure_observation(raw_observation, context)
        
        # 2. Find the exact matching metric in the new output
        new_m = next((m for m in new_measurements if m.definition.id == old_measurement.definition.id 
                      and m.provenance.target_entity == old_measurement.provenance.target_entity), None)
                      
        if not new_m:
            logger.warning(f"V2 Logic no longer emits {old_measurement.definition.id}. Requires deprecation handler.")
            return None
            
        # 3. Quality Gate: The Divergence Check
        is_safe, drift = self.quality.check_divergence(old_measurement.value, new_m.value)
        if not is_safe:
            logger.error(f"BLOCKED: Recompute of {old_measurement.id} drifted by {drift*100}%. Manual intervention required.")
            return None # Fail safe. Do not commit to DB.
            
        # 4. Immutability: Establish Cryptographic Lineage
        # We NEVER update the old measurement. We create a new one pointing to the old one.
        new_id = str(uuid.uuid4())
        
        # Merge new attributes but establish lineage
        metadata = dict(new_m.metadata)
        metadata["supersedes_id"] = old_measurement.id
        
        new_m = replace(new_m, id=new_id, metadata=metadata)
        
        # 5. The Audit Trail
        audit_record = RecomputeAuditRecord(
            audit_id=str(uuid.uuid4()),
            timestamp=datetime.now(UTC),
            old_measurement_id=old_measurement.id,
            new_measurement_id=new_m.id,
            old_logic_version=getattr(old_measurement, 'version', '1.0.0'),
            new_logic_version=getattr(new_m, 'version', '2.0.0'),
            old_value=old_measurement.value,
            new_value=new_m.value,
            percentage_drift=drift,
            authorized_by="system_v2_migration",
            reason="Algorithm upgrade to sanitized heuristics."
        )
        
        # 6. Commit (Assume these are passed to an atomic Unit of Work / Transaction manager)
        self.audit.log_recompute(audit_record)
        
        # Mocking store save in this architectural proof
        if hasattr(self.store, 'save'):
            self.store.save(new_m)
        
        return new_m


