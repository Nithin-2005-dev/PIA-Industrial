from app.concentration.concentration_report import (
    ConcentrationReport,
)

from app.coverage.coverage_report import (
    CoverageReport,
)

from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.health.policies.organizational_health_policy import (
    OrganizationalHealthPolicy,
)

from app.risk.bus_factor import (
    BusFactor,
)

from app.risk.risk_level import (
    RiskLevel,
)


def main():

    coverage_reports = [

        CoverageReport(
            module_ref=EntityRef(
                id="auth.py",
                type=EntityType.FILE,
            ),
            expert_count=4,
            total_expertise=320,
            coverage_score=80,
            coverage_level="STRONG",
        ),

        CoverageReport(
            module_ref=EntityRef(
                id="payments.py",
                type=EntityType.FILE,
            ),
            expert_count=1,
            total_expertise=20,
            coverage_score=10,
            coverage_level="WEAK",
        ),
    ]

    concentration_reports = [

        ConcentrationReport(
            module_ref=EntityRef(
                id="auth.py",
                type=EntityType.FILE,
            ),
            expert_count=4,
            concentration_score=0.30,
            concentration_level="LOW",
        ),

        ConcentrationReport(
            module_ref=EntityRef(
                id="payments.py",
                type=EntityType.FILE,
            ),
            expert_count=1,
            concentration_score=0.98,
            concentration_level="HIGH",
        ),
    ]

    bus_factor_reports = [

        BusFactor(
            module_ref=EntityRef(
                id="auth.py",
                type=EntityType.FILE,
            ),
            value=4,
            coverage=100,
            risk_level=RiskLevel.LOW,
        ),

        BusFactor(
            module_ref=EntityRef(
                id="payments.py",
                type=EntityType.FILE,
            ),
            value=1,
            coverage=100,
            risk_level=RiskLevel.HIGH,
        ),
    ]

    reports = (
        OrganizationalHealthPolicy()
        .evaluate(
            coverage_reports,
            concentration_reports,
            bus_factor_reports,
        )
    )

    print(
        "\n=== HEALTH INDEX ===\n"
    )

    for report in reports:

        print(
            f"Module: "
            f"{report.module_ref.id}"
        )

        print(
            f"Health Score: "
            f"{report.health_score:.2f}"
        )

        print(
            f"Health Level: "
            f"{report.health_level}"
        )

        print(
            f"Coverage Score: "
            f"{report.coverage_score:.2f}"
        )

        print(
            f"Concentration Score: "
            f"{report.concentration_score:.2f}"
        )

        print(
            f"Bus Factor: "
            f"{report.bus_factor}"
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()