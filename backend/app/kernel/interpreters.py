from typing import Any, Optional, Dict, List
from dataclasses import asdict, is_dataclass
from .models import (
    DomainReport, Explanation, HealthReport, ForecastReport, 
    OwnershipReport, BusFactorReport, KnowledgeGraphReport, 
    TopContributorReport, RepositoryReport, CausalReport,
    SimulationReport, DeveloperDepartureSimulationReport,
    OwnershipSimulationReport, ArchitectureSimulationReport,
    ForecastSimulationReport, RiskSimulationReport
)

class ExecutiveSummaryBuilder:
    @staticmethod
    def build(report_type: str, data: Any) -> Optional[dict]:
        return {
            "Key Findings": f"Deterministic findings for {report_type}.",
            "Key Risks": "Identified from platform output.",
            "Recommended Actions": ["Review metrics", "Adjust allocations"],
            "Confidence": "High",
            "Business Impact": "Medium"
        }

class CapabilityInterpreter:
    def interpret(self, raw_data: Any, contract: Any) -> DomainReport:
        raise NotImplementedError

class TopContributorsInterpreter(CapabilityInterpreter):
    def interpret(self, raw_data: Any, contract: Any) -> DomainReport:
        d = asdict(raw_data) if is_dataclass(raw_data) else (raw_data if isinstance(raw_data, dict) else {})
        contributors = d.get("contributors", []) if isinstance(d, dict) else []
        if isinstance(raw_data, list):
            contributors = raw_data
        
        # Format the top contributors
        formatted = [{"name": c.get("name", "Unknown"), "commits": c.get("commits", 0)} for c in contributors if isinstance(c, dict)]
        return TopContributorReport(
            contributors=formatted,
            executive_summary=ExecutiveSummaryBuilder.build("TopContributors", raw_data)
        )

class OwnershipInterpreter(CapabilityInterpreter):
    def interpret(self, raw_data: Any, contract: Any) -> DomainReport:
        from app.kernel.enrichers.ownership_enricher import OwnershipEnricher
        return OwnershipEnricher().enrich(
            raw_data=raw_data,
            contract=contract,
            executive_summary=ExecutiveSummaryBuilder.build("Ownership", raw_data) or ""
        )

class BusFactorInterpreter(CapabilityInterpreter):
    def interpret(self, raw_data: Any, contract: Any) -> DomainReport:
        from app.kernel.enrichers.bus_factor_enricher import BusFactorEnricher
        return BusFactorEnricher().enrich(
            raw_data=raw_data,
            contract=contract,
            executive_summary=ExecutiveSummaryBuilder.build("BusFactor", raw_data) or ""
        )

class HealthInterpreter(CapabilityInterpreter):
    def interpret(self, raw_data: Any, contract: Any) -> DomainReport:
        d = asdict(raw_data) if is_dataclass(raw_data) else (raw_data if isinstance(raw_data, dict) else {})
        health_obj = d.get("health", {})
        
        score = 0.0
        critical = 0
        if isinstance(health_obj, dict):
            score = health_obj.get("average_health", 0.0)
            critical = health_obj.get("critical_count", 0)
        else:
            score = getattr(health_obj, "average_health", 0.0)
            critical = getattr(health_obj, "critical_count", 0)
            
        return HealthReport(
            overall_health=float(score),
            health_grade="A" if score > 0.8 else ("B" if score > 0.6 else "C"),
            critical_modules=critical,
            executive_summary=ExecutiveSummaryBuilder.build("Health", raw_data)
        )

class ForecastInterpreter(CapabilityInterpreter):
    def interpret(self, raw_data: Any, contract: Any) -> DomainReport:
        d = asdict(raw_data) if is_dataclass(raw_data) else (raw_data if isinstance(raw_data, dict) else {})
        return ForecastReport(
            health_forecast=d.get("metrics", {}),
            executive_summary=ExecutiveSummaryBuilder.build("Forecast", raw_data)
        )

class CausalInterpreter(CapabilityInterpreter):
    def interpret(self, raw_data: Any, contract: Any) -> DomainReport:
        d = asdict(raw_data) if is_dataclass(raw_data) else (raw_data if isinstance(raw_data, dict) else {})
        cause = d.get("primary_cause", "Unknown cause")
        return CausalReport(
            primary_root_cause=str(cause),
            executive_summary=ExecutiveSummaryBuilder.build("CausalAnalysis", raw_data)
        )

class KnowledgeGraphInterpreter(CapabilityInterpreter):
    def interpret(self, raw_data: Any, contract: Any) -> DomainReport:
        from app.kernel.enrichers.knowledge_graph_enricher import KnowledgeGraphEnricher
        return KnowledgeGraphEnricher().enrich(
            raw_data=raw_data,
            contract=contract,
            executive_summary=ExecutiveSummaryBuilder.build("KnowledgeGraph", raw_data) or ""
        )

class SimulationInterpreter(CapabilityInterpreter):
    def interpret(self, raw_data: Any, contract: Any) -> DomainReport:
        d = asdict(raw_data) if is_dataclass(raw_data) else (raw_data if isinstance(raw_data, dict) else {})
        
        if contract.id == "cap_dev_departure_simulation":
            return DeveloperDepartureSimulationReport(
                scenario="Developer Departure",
                executive_summary=ExecutiveSummaryBuilder.build("DeveloperDepartureSimulation", raw_data)
            )
        elif contract.id == "cap_ownership_simulation":
            return OwnershipSimulationReport(
                scenario="Ownership Change",
                executive_summary=ExecutiveSummaryBuilder.build("OwnershipSimulation", raw_data)
            )
        elif contract.id == "cap_architecture_simulation":
            return ArchitectureSimulationReport(
                scenario="Architecture Change",
                executive_summary=ExecutiveSummaryBuilder.build("ArchitectureSimulation", raw_data)
            )
        elif contract.id == "cap_forecast_simulation":
            return ForecastSimulationReport(
                scenario="Forecast Scenario",
                executive_summary=ExecutiveSummaryBuilder.build("ForecastSimulation", raw_data)
            )
        elif contract.id == "cap_risk_simulation":
            return RiskSimulationReport(
                scenario="Risk Scenario",
                executive_summary=ExecutiveSummaryBuilder.build("RiskSimulation", raw_data)
            )
        
        return SimulationReport(
            scenario="Generic Simulation",
            executive_summary=ExecutiveSummaryBuilder.build("Simulation", raw_data)
        )

# Factory map
INTERPRETERS = {
    "cap_top_contributors": TopContributorsInterpreter(),
    "cap_ownership": OwnershipInterpreter(),
    "cap_bus_factor": BusFactorInterpreter(),
    "cap_health": HealthInterpreter(),
    "cap_forecast": ForecastInterpreter(),
    "cap_causal_analysis": CausalInterpreter(),
    "cap_knowledge_graph": KnowledgeGraphInterpreter(),
    "cap_dev_departure_simulation": SimulationInterpreter(),
    "cap_ownership_simulation": SimulationInterpreter(),
    "cap_architecture_simulation": SimulationInterpreter(),
    "cap_forecast_simulation": SimulationInterpreter(),
    "cap_risk_simulation": SimulationInterpreter(),
    "cap_simulation": SimulationInterpreter(),
}
