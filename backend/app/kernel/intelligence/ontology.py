from typing import Any, Dict, List, Optional
import dataclasses
from enum import Enum

class RiskDomain(Enum):
    TECHNICAL = "technical"
    BUSINESS = "business"
    OPERATIONAL = "operational"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"

@dataclasses.dataclass(frozen=True)
class OntologyCategory:
    id: str
    name: str
    domain: RiskDomain
    parent_id: Optional[str] = None
    description: str = ""

class CoreOntology:
    """
    Core Kernel Ontology for Risk and Impact mapping.
    Allows generic rules to map Technical metrics to Business outcomes.
    """
    def __init__(self):
        self._categories: Dict[str, OntologyCategory] = {}
        self._load_core()
        
    def _load_core(self):
        # Operational Risk Chain
        self.register(OntologyCategory("risk_operational", "Operational Risk", RiskDomain.OPERATIONAL))
        self.register(OntologyCategory("risk_continuity", "Continuity Risk", RiskDomain.OPERATIONAL, parent_id="risk_operational"))
        self.register(OntologyCategory("risk_knowledge_concentration", "Knowledge Concentration", RiskDomain.TECHNICAL, parent_id="risk_continuity"))
        
        # Financial Risk Chain
        self.register(OntologyCategory("risk_financial", "Financial Risk", RiskDomain.FINANCIAL))
        self.register(OntologyCategory("risk_maintenance_cost", "High Maintenance Cost", RiskDomain.FINANCIAL, parent_id="risk_financial"))
        self.register(OntologyCategory("risk_technical_debt", "Technical Debt", RiskDomain.TECHNICAL, parent_id="risk_maintenance_cost"))

    def register(self, category: OntologyCategory):
        self._categories[category.id] = category
        
    def get_lineage(self, category_id: str) -> List[OntologyCategory]:
        """Walks up the ontology tree from a specific risk to its core business domain."""
        lineage = []
        current = category_id
        while current and current in self._categories:
            cat = self._categories[current]
            lineage.append(cat)
            current = cat.parent_id
        return lineage
