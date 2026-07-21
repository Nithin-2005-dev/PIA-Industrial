import os
from time import perf_counter

from pathlib import Path
from contextlib import redirect_stdout


from datetime import UTC
from datetime import datetime

from app.adapters.github.adapter import (
    GitHubAdapter,
)

from app.adapters.github.rest_gateway import (
    GitHubRestGateway,
)

from app.bootstrap.intelligence_context import (
    IntelligenceContext,
)

from app.estimator.estimation_context import (
    EstimationContext,
)

from app.estimator.expertise_estimator import (
    ExpertiseEstimator,
)

from app.estimator.expertise_projection import (
    ExpertiseProjection,
)

from app.estimator.policies.exponential_decay_policy import (
    ExponentialDecayPolicy,
)

from app.estimator.policies.rule_expertise_scoring_policy import (
    RuleExpertiseScoringPolicy,
)

from app.extractor.expertise_extractor import (
    ExpertiseExtractor,
)

from app.extractor.policies.github_commit_strength_policy import (
    GitHubCommitStrengthPolicy,
)

from app.ports.event_query import (
    EventQuery,
)


def line():

    print("-" * 80)


def heading(title):

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def main():

    heading(
        "PIA COMPLETE PIPELINE"
    )

    token = os.getenv(
        "GITHUB_TOKEN"
    )

    if token is None:

        raise RuntimeError(
            "GITHUB_TOKEN environment variable not found."
        )

    repository = os.getenv(
        "PIA_REPOSITORY",
        "facebook/react",
    )

    commit_limit = int(
        os.getenv(
            "PIA_COMMITS",
            "10",
        )
    )

    print()
    print(f"Repository   : {repository}")
    print(f"Commit Limit : {commit_limit}")
    line()

    print("[1/6] Initializing services...")

    gateway = GitHubRestGateway(
        token=token,
    )

    adapter = GitHubAdapter(
        gateway=gateway,
    )

    extractor = ExpertiseExtractor(
        GitHubCommitStrengthPolicy(),
    )

    estimator = ExpertiseEstimator(
        RuleExpertiseScoringPolicy(),
        ExponentialDecayPolicy(),
    )

    projection = ExpertiseProjection(
        estimator,
    )

    estimation_context = (
        EstimationContext(
            current_time=datetime.now(
                UTC,
            ),
            learning_rate=1.0,
        )
    )

    print("✓ Services initialized")

    line()

    print("[2/6] Collecting GitHub commits...")

    start = perf_counter()

    query = EventQuery(
        identifier=repository,
        filters={
            "per_page": commit_limit,
        },
    )

    events = adapter.collect(
        query
    )

    elapsed = perf_counter() - start

    print(
        f"✓ {len(events)} commits collected "
        f"({elapsed:.2f}s)"
    )

    line()

    print("[3/6] Extracting evidence...")

    start = perf_counter()

    total_evidence = 0

    developers = set()

    modules = set()

    processed = 0

    for event in events:

        processed += 1

        print(
            f"\rProcessing event "
            f"{processed}/{len(events)}",
            end="",
            flush=True,
        )

        evidence_list = extractor.extract(
            event
        )

        total_evidence += len(
            evidence_list
        )

        for evidence in evidence_list:

            projection.apply(
                evidence,
                estimation_context,
            )

            developers.add(
                evidence.subject_ref.id
            )

            modules.add(
                evidence.object_ref.id
            )

    print()

    elapsed = perf_counter() - start

    print(
        f"✓ Evidence extraction completed "
        f"({elapsed:.2f}s)"
    )

    line()

    print("[4/6] Building expertise projection...")

    print(
        f"Developers discovered : "
        f"{len(developers)}"
    )

    print(
        f"Modules discovered    : "
        f"{len(modules)}"
    )

    print(
        f"Evidence generated    : "
        f"{total_evidence}"
    )

    line()

    print("[5/6] Creating Intelligence Context...")

    intelligence = IntelligenceContext(
        projection
    )

    print("✓ Intelligence initialized")

    line()

    print("[6/6] Pipeline Summary")

    print(
        f"Repository : {repository}"
    )

    print(
        f"Events     : {len(events)}"
    )

    print(
        f"Evidence   : {total_evidence}"
    )

    print(
        f"Developers : {len(developers)}"
    )

    print(
        f"Modules    : {len(modules)}"
    )

    heading(
        "PIPELINE PASSED"
    )

    estimates = projection.all_estimates()

    print(
        f"Total Expertise Estimates : "
        f"{len(estimates)}"
    )

    line()

    print(
        "Top Expertise Estimates\n"
    )

    estimates = sorted(
        estimates,
        key=lambda estimate: (
            estimate.raw_score
            * estimate.confidence
        ),
        reverse=True,
    )

    for estimate in estimates[:20]:

        print(
            f"Developer : "
            f"{estimate.developer_ref.id}"
        )

        print(
            f"Module    : "
            f"{estimate.module_ref.id}"
        )

        print(
            f"Raw Score : "
            f"{estimate.raw_score:.2f}"
        )

        print(
            f"Confidence: "
            f"{estimate.confidence:.2f}"
        )

        print(
            f"Effective : "
            f"{estimate.raw_score * estimate.confidence:.2f}"
        )

        line()

    heading(
        "EVENT SUMMARY"
    )

    author_count = {}

    module_count = {}

    for event in events:

        author = event.actor_ref.id

        author_count[author] = (
            author_count.get(
                author,
                0,
            )
            + 1
        )

        for target in event.target_refs:

            module_name = target.id

            module_count[module_name] = (
                module_count.get(
                    module_name,
                    0,
                )
                + 1
            )

    print(
        "Top Authors\n"
    )

    for author, count in sorted(
        author_count.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:10]:

        print(
            f"{author:<25}"
            f"{count}"
        )

    line()

    print(
        "Top Modified Modules\n"
    )

    for module_name, count in sorted(
        module_count.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:20]:

        print(
            f"{module_name:<60}"
            f"{count}"
        )

    heading(
        "PROJECTION STATISTICS"
    )

    print(
        f"Developers Learned : "
        f"{len(developers)}"
    )

    print(
        f"Modules Learned    : "
        f"{len(modules)}"
    )

    print(
        f"Expertise Estimates: "
        f"{len(estimates)}"
    )

    print(
        f"Evidence Generated : "
        f"{total_evidence}"
    )

    line()

    print(
        "Top Developers by Expertise\n"
    )

    developer_scores = {}

    for estimate in estimates:

        developer = (
            estimate.developer_ref.id
        )

        score = (
            estimate.raw_score
            * estimate.confidence
        )

        developer_scores[developer] = (
            developer_scores.get(
                developer,
                0.0,
            )
            + score
        )

    for developer, score in sorted(
        developer_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:10]:

        print(
            f"{developer:<25}"
            f"{score:.2f}"
        )

    line()

    print(
        "Top Modules by Expertise\n"
    )

    module_scores = {}

    for estimate in estimates:

        module_name = (
            estimate.module_ref.id
        )

        score = (
            estimate.raw_score
            * estimate.confidence
        )

        module_scores[module_name] = (
            module_scores.get(
                module_name,
                0.0,
            )
            + score
        )

    for module_name, score in sorted(
        module_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:20]:

        print(
            f"{module_name:<60}"
            f"{score:.2f}"
        )

    heading(
        "INTELLIGENCE CONTEXT"
    )

    print(
        "Initialized Services\n"
    )

    print("✓ Ownership Service")
    print("✓ Successor Service")
    print("✓ Coverage Service")
    print("✓ Concentration Service")
    print("✓ Bus Factor Service")
    print("✓ Health Service")
    print("✓ History Service")
    print("✓ Forecast Pipeline")
    print("✓ Future Risk Pipeline")
    print("✓ Organization Dashboard")
    print("✓ Simulation Services")
    print("✓ Scenario Services")

    heading(
        "OWNERSHIP ANALYSIS"
    )

    print(
        "Top Module Owners\n"
    )

    shown = 0

    for module_name in sorted(modules):

        if shown >= 10:
            break

        owners = (
            intelligence
            .ownership_service
            .owners_of(
                module_name
            )
        )

        if not owners:
            continue

        print(
            f"\nModule : {module_name}"
        )

        line()

        for owner in owners:

            print(
                f"{owner.owner_ref.id:<25}"
                f"{owner.ownership_percentage:>8.2f}%"
            )

        shown += 1
    
    heading(
        "SUCCESSOR ANALYSIS"
    )

    shown = 0

    for module_name in sorted(modules):

        if shown >= 10:
            break

        successors = (
            intelligence
            .successor_service
            .recommend(
                module_name,
                limit=3,
            )
        )

        if not successors:
            continue

        print(
            f"\nModule : {module_name}"
        )

        line()

        for successor in successors:

            print(
                f"Rank {successor.rank:<2}"
                f"{successor.developer_ref.id:<25}"
                f"Score {successor.score:.2f}"
            )

        shown += 1
    
    
    heading(
        "COVERAGE ANALYSIS"
    )

    estimates = (
        projection.all_estimates()
    )

    coverage_reports = (
        intelligence
        .coverage_service
        .analyze(
            estimates
        )
    )

    coverage_reports = sorted(
        coverage_reports,
        key=lambda report: (
            report.coverage_score
        ),
        reverse=True,
    )

    print(
        "Top Covered Modules\n"
    )

    for report in coverage_reports[:20]:

        print(
            f"Module     : "
            f"{report.module_ref.id}"
        )

        print(
            f"Experts    : "
            f"{report.expert_count}"
        )

        print(
            f"Coverage   : "
            f"{report.coverage_score:.2f}"
        )

        print(
            f"Level      : "
            f"{report.coverage_level}"
        )

        line()
        
    heading(
        "CONCENTRATION ANALYSIS"
    )

    concentration_reports = (
        intelligence
        .concentration_service
        .analyze(
            estimates
        )
    )

    concentration_reports = sorted(
        concentration_reports,
        key=lambda report: (
            report.concentration_score
        ),
        reverse=True,
    )

    print(
        "Highest Concentration Modules\n"
    )

    for report in concentration_reports[:20]:

        print(
            f"Module        : "
            f"{report.module_ref.id}"
        )

        print(
            f"Experts       : "
            f"{report.expert_count}"
        )

        print(
            f"Concentration : "
            f"{report.concentration_score:.2f}"
        )

        print(
            f"Level         : "
            f"{report.concentration_level}"
        )

        line()
        
    
    heading(
        "BUS FACTOR ANALYSIS"
    )

    bus_factor_reports = []

    print(
        "Bus Factor by Module\n"
    )

    for report in coverage_reports:

        bus_factor = (
            intelligence
            .bus_factor_service
            .analyze(
                report.module_ref.id
            )
        )

        bus_factor_reports.append(
            bus_factor
        )

        print(
            f"Module     : "
            f"{bus_factor.module_ref.id}"
        )

        print(
            f"Bus Factor : "
            f"{bus_factor.value}"
        )

        print(
            f"Coverage   : "
            f"{bus_factor.coverage:.2f}"
        )

        print(
            f"Risk Level : "
            f"{bus_factor.risk_level}"
        )

        line()
    

    heading(
        "HEALTH ANALYSIS"
    )

    health_reports = (
        intelligence
        .health_service
        .analyze(
            coverage_reports,
            concentration_reports,
            bus_factor_reports,
        )
    )

    health_reports = sorted(
        health_reports,
        key=lambda report: (
            report.health_score
        ),
        reverse=True,
    )

    print(
        "Module Health\n"
    )

    for report in health_reports:

        print(
            f"Module          : "
            f"{report.module_ref.id}"
        )

        print(
            f"Health Score    : "
            f"{report.health_score:.2f}"
        )

        print(
            f"Health Level    : "
            f"{report.health_level}"
        )

        print(
            f"Coverage Score  : "
            f"{report.coverage_score:.2f}"
        )

        print(
            f"Concentration   : "
            f"{report.concentration_score:.2f}"
        )

        print(
            f"Bus Factor      : "
            f"{report.bus_factor}"
        )

        line()
    
    heading(
        "ORGANIZATION DASHBOARD"
    )

    dashboard = (
        intelligence
        .organization_dashboard_service
        .dashboard()
    )

    print(
        "Organization Health\n"
    )

    print(
        f"Average Health   : "
        f"{dashboard.health.average_health:.2f}"
    )

    print(
        f"Best Health      : "
        f"{dashboard.health.best_health:.2f}"
    )

    print(
        f"Worst Health     : "
        f"{dashboard.health.worst_health:.2f}"
    )

    print(
        f"Healthy Modules  : "
        f"{dashboard.health.healthy_modules}"
    )

    print(
        f"Warning Modules  : "
        f"{dashboard.health.warning_modules}"
    )

    print(
        f"Critical Modules : "
        f"{dashboard.health.critical_modules}"
    )

    print(
        f"Total Modules    : "
        f"{dashboard.health.total_modules}"
    )

    line()

    print(
        "Top Organizational Risks\n"
    )

    for risk in dashboard.risks:

        print(
            f"Rank      : "
            f"{risk.rank}"
        )

        print(
            f"Module    : "
            f"{risk.module_ref.id}"
        )

        print(
            f"Health    : "
            f"{risk.health_score:.2f}"
        )

        print(
            f"Future    : "
            f"{risk.future_risk_score:.2f}"
        )

        print(
            f"Severity  : "
            f"{risk.severity_level}"
        )

        line()

    print(
        "Weakest Readiness\n"
    )

    for readiness in (
        dashboard.readiness
    ):

        print(
            f"Rank      : "
            f"{readiness.rank}"
        )

        print(
            f"Module    : "
            f"{readiness.module_ref.id}"
        )

        print(
            f"Readiness : "
            f"{readiness.readiness_score:.2f}"
        )

        line()

    print(
        "Knowledge Transfer Opportunities\n"
    )

    for transfer in (
        dashboard.transfers
    ):

        print(
            f"Rank      : "
            f"{transfer.rank}"
        )

        print(
            f"Module    : "
            f"{transfer.module_ref.id}"
        )

        print(
            f"Mentor    : "
            f"{transfer.mentor_ref.id}"
        )

        print(
            f"Learner   : "
            f"{transfer.learner_ref.id}"
        )

        print(
            f"Priority  : "
            f"{transfer.priority_score:.2f}"
        )

        line()

    heading(
        "FINAL PIPELINE SUMMARY"
    )

    print(
        f"Repository           : {repository}"
    )

    print(
        f"Events Collected     : {len(events)}"
    )

    print(
        f"Evidence Generated   : {total_evidence}"
    )

    print(
        f"Developers Learned   : {len(developers)}"
    )

    print(
        f"Modules Learned      : {len(modules)}"
    )

    print(
        f"Expertise Estimates  : {len(estimates)}"
    )

    print(
        f"Coverage Reports     : {len(coverage_reports)}"
    )

    print(
        f"Concentration Reports: {len(concentration_reports)}"
    )

    print(
        f"Bus Factors          : {len(bus_factor_reports)}"
    )

    print(
        f"Health Reports       : {len(health_reports)}"
    )

    print()

    print(
        "✓ GitHub Adapter"
    )

    print(
        "✓ Evidence Extraction"
    )

    print(
        "✓ Expertise Projection"
    )

    print(
        "✓ Ownership Analysis"
    )

    print(
        "✓ Successor Analysis"
    )

    print(
        "✓ Coverage Analysis"
    )

    print(
        "✓ Concentration Analysis"
    )

    print(
        "✓ Bus Factor Analysis"
    )

    print(
        "✓ Health Analysis"
    )

    print(
        "✓ Organization Dashboard"
    )

    heading(
        "PIA END-TO-END PIPELINE PASSED"
    )
if __name__ == "__main__":

    import sys

    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"pipeline_{timestamp}.txt"

    class Tee:
        def __init__(self, *streams):
            self.streams = streams

        def write(self, data):
            for stream in self.streams:
                stream.write(data)

        def flush(self):
            for stream in self.streams:
                stream.flush()

    with output_file.open("w", encoding="utf-8") as file:
        with redirect_stdout(Tee(sys.stdout, file)):
            main()

    print(f"\nOutput saved to: {output_file}")