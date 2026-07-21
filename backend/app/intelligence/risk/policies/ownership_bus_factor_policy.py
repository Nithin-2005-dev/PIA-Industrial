from app.intelligence.legacy.ownership_estimate import (
    OwnershipEstimate,
)

from app.intelligence.risk.bus_factor import (
    BusFactor,
)

from app.intelligence.risk.risk_level import (
    RiskLevel,
)

from .bus_factor_policy import (
    BusFactorPolicy,
)


class OwnershipBusFactorPolicy(
    BusFactorPolicy
):

    HIGH_RISK_THRESHOLD = 1
    MEDIUM_RISK_THRESHOLD = 2

    def __init__(
        self,
        coverage_threshold: float = 0.8,
    ):
        self._coverage_threshold = (
            coverage_threshold
        )

    def calculate(
        self,
        ownership: list[OwnershipEstimate],
    ) -> BusFactor:

        if not ownership:

            raise ValueError(
                "Ownership list cannot be empty."
            )

        sorted_ownership = sorted(
            ownership,
            key=lambda owner: (
                owner.ownership_percentage
            ),
            reverse=True,
        )

        coverage = 0.0

        count = 0

        for owner in sorted_ownership:

            coverage += (
                owner.ownership_percentage
            )
            count += 1

            # Relax the strict threshold: ensure we count at least anyone who is a primary/secondary owner,
            # or continue until we hit the threshold.
            if coverage >= self._coverage_threshold:
                # But don't exclude a secondary owner just because they put us over 80%.
                # Look ahead to see if the next owner has significant percentage (e.g. > 15%).
                pass # Handled below by looking at the remaining list.

        # New approach: count any owner with > 15% ownership.
        # This matches the ExpertiseOwnershipPolicy's SECONDARY threshold.
        count = sum(1 for owner in sorted_ownership if owner.ownership_percentage >= 0.15)
        # Fallback in case everyone is tiny
        if count == 0 and sorted_ownership:
            count = 1

        # Recalculate true coverage of the bus factor group
        coverage = sum(owner.ownership_percentage for owner in sorted_ownership[:count])

        # Calculate scientific concentration metrics
        import math
        shannon_entropy = 0.0
        hhi = 0.0
        
        for owner in sorted_ownership:
            p = owner.ownership_percentage
            if p > 0:
                shannon_entropy -= p * math.log2(p)
                hhi += p * p

        # Gini Coefficient
        n = len(sorted_ownership)
        if n > 1:
            # sorted_ownership is sorted descending, we want ascending for standard Gini formula
            ascending_ownership = list(reversed(sorted_ownership))
            cumulative_sum = 0.0
            cumulative_weighted_sum = 0.0
            
            for i, owner in enumerate(ascending_ownership, 1):
                cumulative_sum += owner.ownership_percentage
                cumulative_weighted_sum += i * owner.ownership_percentage
                
            gini_coefficient = (2.0 * cumulative_weighted_sum) / (n * cumulative_sum) - (n + 1.0) / n
        else:
            gini_coefficient = 0.0

        if count <= self.HIGH_RISK_THRESHOLD:

            risk_level = (
                RiskLevel.HIGH
            )

        elif count <= self.MEDIUM_RISK_THRESHOLD:

            risk_level = (
                RiskLevel.MEDIUM
            )

        else:

            risk_level = (
                RiskLevel.LOW
            )

        return BusFactor(
            module_ref=(
                ownership[0].module_ref
            ),
            value=count,
            coverage=coverage,
            shannon_entropy=shannon_entropy,
            gini_coefficient=gini_coefficient,
            hhi=hhi,
            uncertainty=0.05, # Default estimation uncertainty
            confidence=0.95,
            risk_level=risk_level,
        )