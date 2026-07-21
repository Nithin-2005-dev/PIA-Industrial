from dataclasses import dataclass


@dataclass(frozen=True)
class OrganizationDashboard:

    health: object

    risks: list

    readiness: list

    transfers: list