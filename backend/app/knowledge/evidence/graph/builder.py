from app.knowledge.evidence.core import EvidencePackage
from app.knowledge.evidence.domain import Evidence
from app.knowledge.evidence.graph.graph import IEvidenceGraphStore
from app.knowledge.evidence.graph.filters import OntologicalStopWordFilter
from app.knowledge.evidence.ontology import EvidenceRelationship


class EvidenceGraphBuilder:

    def __init__(
        self,
        store: IEvidenceGraphStore,
        stop_word_filter: OntologicalStopWordFilter | None = None,
    ):
        self._store = store
        self._filter = stop_word_filter or OntologicalStopWordFilter()

    def build(self, package: EvidencePackage) -> IEvidenceGraphStore:
        """
        Builds the physical graph topology from the Evidence Package.
        Safely handles supersession (Landmine 5) and God Nodes (Landmine 4).
        """
        for evidence in package.evidence:
            self._process_evidence(evidence)
        return self._store

    def _process_evidence(self, evidence: Evidence) -> None:
        # Handle supersession: Delete superseded graph structures
        supersedes_id = evidence.metadata.get("supersedes_id")
        if supersedes_id:
            self._store.remove_evidence(supersedes_id)
            
        # Add core nodes (Evidence -> Concept/Measurements)
        self._store.add_evidence(evidence)

        # Build dynamic ontological relationships from underlying measurements
        for ref in evidence.supporting_measurements:
            target = ref.metadata.get("target")
            actor = ref.metadata.get("actor")
            
            # Use Z-Score or quality score as weight if needed, default to confidence
            weight = max(0.001, float(ref.metadata.get("z_score", ref.confidence)))
            
            if target and actor:
                # Apply Ontological Stop-Word Filter to prevent "God Nodes"
                if self._filter.should_drop(target):
                    continue
                
                # Determine relationship based on concept
                concept = ref.name.lower()
                
                if "bug" in concept or "incident" in concept:
                    rel_enum = EvidenceRelationship.INTRODUCED_BUG_IN
                else:
                    rel_enum = EvidenceRelationship.AUTHORED
                
                # Add relationship to the store
                self._store.add_relationship(
                    source_id=actor,
                    target_id=target,
                    relationship=rel_enum,
                    origin_id=evidence.evidence_id
                )
                
            # If the measurement is a pure dependency edge (e.g. Code_Dependency)
            dependency = ref.metadata.get("dependency")
            if target and dependency:
                if self._filter.should_drop(dependency) or self._filter.should_drop(target):
                    continue
                self._store.add_relationship(
                    source_id=target,
                    target_id=dependency,
                    relationship=EvidenceRelationship.DEPENDS_ON,
                    origin_id=evidence.evidence_id
                )
