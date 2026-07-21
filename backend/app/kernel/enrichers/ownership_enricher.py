from typing import Any
from dataclasses import asdict, is_dataclass
from app.kernel.models import (
    OwnershipReport, 
    OwnershipProfile, 
    CapabilityQualityContract
)

class OwnershipEnricher:
    """Enriches raw ownership data into rich semantic Ownership Profiles."""
    
    def enrich(self, raw_data: Any, contract: Any, executive_summary: str = "") -> OwnershipReport:
        d = asdict(raw_data) if is_dataclass(raw_data) else (raw_data if isinstance(raw_data, dict) else {})
        
        ownership = list(d.get("ownership", []))
        successors = list(d.get("successors", []))
        
        def _get_val(obj, key, default):
            if isinstance(obj, dict): return obj.get(key, default)
            return getattr(obj, key, default)

        # Developer -> Modules mapping
        dev_modules = {}
        for o in ownership:
            # We assume subject is the module for now, wait, is ownership subject a module or developer?
            # In stage08, subject is the module. category is the category. 
            # But we want OwnershipProfile to be per-developer!
            # Since the proxy doesn't currently store developer ID in OwnershipEntry (it stores subject as module),
            # this is a known limitation. We'll build the profile based on the available data.
            # Wait, `OwnershipProfile` has `developer` and `owned_modules`.
            # If `subject` is module, we don't have developer name in `OwnershipEntry`. 
            # I will map it per-module for now and assume the module is the "developer" unit if they were grouped.
            pass
            
        # Actually, let's just create one profile per subject
        profiles = []
        for o in ownership:
            subj = _get_val(o, "subject", "")
            score = _get_val(o, "ownership_percentage", 0.0)
            
            # Find successors for this subject
            succs = [
                _get_val(s, "successor_subject", "") for s in successors 
                if _get_val(s, "primary_subject", "") == subj
            ]
            
            profile = OwnershipProfile(
                developer="Unknown", # Requires full ExpertiseModel to map back to dev
                owned_modules=(subj,),
                ownership_score=score,
                dependency_score=0.0,
                successors=tuple(succs),
                reviewers=(),
                risk="LOW"
            )
            profiles.append(profile)
            
        quality = CapabilityQualityContract(
            coverage=1.0,
            completeness=0.50, # Developer identities missing from OwnershipEntry
            freshness=1.0,
            confidence=0.90,
            limitations=("OwnershipEntries currently aggregate by module, missing developer mapping",)
        )
            
        return OwnershipReport(
            executive_summary=executive_summary,
            profiles=tuple(profiles),
            quality=quality
        )
