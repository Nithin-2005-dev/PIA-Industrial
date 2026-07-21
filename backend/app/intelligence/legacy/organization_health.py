from dataclasses import dataclass


@dataclass(frozen=True)
class OrganizationHealth:

    average_health: float

    best_health: float

    worst_health: float

    healthy_modules: int

    warning_modules: int

    critical_modules: int

    total_modules: int