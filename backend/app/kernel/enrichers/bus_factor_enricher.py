from typing import Any
from dataclasses import asdict, is_dataclass
from app.kernel.models import (
    BusFactorReport, 
    ModuleRiskProfile, 
    CapabilityQualityContract
)

class BusFactorEnricher:
    """Enriches raw bus factor data into rich semantic Module Risk Profiles."""
    
    def enrich(self, raw_data: Any, contract: Any, executive_summary: str = "") -> BusFactorReport:
        d = asdict(raw_data) if is_dataclass(raw_data) else (raw_data if isinstance(raw_data, dict) else {})
        
        bus_factors = list(d.get("bus_factors", []))
        risks = list(d.get("knowledge_risks", []))
        ownership = list(d.get("ownership", []))
        concentration = list(d.get("concentration", []))
        
        # Build maps for easy lookup
        def _get_val(obj, key, default):
            if isinstance(obj, dict): return obj.get(key, default)
            return getattr(obj, key, default)

        risk_map = { _get_val(r, "subject", ""): r for r in risks }
        conc_map = { _get_val(c, "subject", ""): _get_val(c, "concentration_score", 0.0) for c in concentration }
        
        # Build list of owners and contributors per subject
        owners_map = {}
        contributors_map = {}
        for o in ownership:
            subj = _get_val(o, "subject", "")
            if subj not in owners_map:
                owners_map[subj] = []
            if subj not in contributors_map:
                contributors_map[subj] = []
                
            level = _get_val(o, "ownership_level", "")
            if level in ("PRIMARY", "SECONDARY"):
                owners_map[subj].append("developer") # Real implementation would need developer ID. For now we just add placeholders or actual IDs if available.
            elif level == "CONTRIBUTOR":
                contributors_map[subj].append("developer")

        profiles = []
        for bf in bus_factors:
            subj = _get_val(bf, "subject", "")
            bf_val = _get_val(bf, "bus_factor", 0)
            cov_val = _get_val(bf, "coverage", 0.0)
            
            r_obj = risk_map.get(subj)
            crit = _get_val(r_obj, "risk_level", "UNKNOWN") if r_obj else "UNKNOWN"
            conc = conc_map.get(subj, 0.0)
            
            profile = ModuleRiskProfile(
                module=subj,
                bus_factor=bf_val,
                owners=tuple(owners_map.get(subj, [])),
                contributors=tuple(contributors_map.get(subj, [])),
                knowledge_concentration=conc,
                criticality=crit,
                coverage=cov_val,
                confidence=0.90
            )
            profiles.append(profile)
            
        quality = CapabilityQualityContract(
            coverage=1.0,
            completeness=0.85,
            freshness=1.0,
            confidence=0.95,
            limitations=("Developer identities are aggregated in raw data",)
        )
        
        return BusFactorReport(
            executive_summary=executive_summary,
            profiles=tuple(profiles),
            quality=quality
        )
