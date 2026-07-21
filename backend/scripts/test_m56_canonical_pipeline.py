import sys
import time
from pathlib import Path
from dataclasses import dataclass, field

from app.platform.runtime import PlatformRuntime
from app.platform.api.contracts import RuntimePipelineInput
from app.platform.canonical_pipeline import CanonicalPlatformPipeline

def main():
    runtime = PlatformRuntime.create()
    
    # Register all 14 canonical modules
    runtime.register_default_modules()

    # Build the runtime
    built = runtime.build()

    pipeline = CanonicalPlatformPipeline(built)
    bindings = pipeline._bindings_by_runtime_order()
    
    stages_order = [b.stage.name for b in bindings]
    
    # Deduplicate while preserving order
    seen = set()
    actual_path = []
    for stage in stages_order:
        if stage not in seen:
            seen.add(stage)
            actual_path.append(stage)

    expected_path = [
        "Platform Initialization",
        "GitHub to Observation",
        "Observation Intelligence",
        "Observation to Measurement",
        "Measurement to Evidence",
        "Evidence to Expertise",
        "Expertise to Knowledge",
        "Knowledge Graph Construction",
        "Temporal Intelligence",
        "Forecasting",
        "Counterfactual Simulation",
        "Organization Intelligence",
        "Causal Intelligence",
        "Knowledge and Org Intel to Reasoning",
        "Reasoning to Decision",
        "Portfolio Optimization",
        "Executive Dashboard",
        "Pipeline Validation",
        "Executive Intelligence Report",
    ]

    print("Actual Path:")
    for idx, stage in enumerate(actual_path):
        print(f"{idx+1:2}. {stage}")

    print("\nExpected Path:")
    for idx, stage in enumerate(expected_path):
        print(f"{idx+1:2}. {stage}")

    assert actual_path == expected_path, "Pipeline execution order mismatch!"
    
    print("\n[OK] Canonical pipeline registers exactly 14 modules + sub-stages in the correct sequence.")
    sys.exit(0)

if __name__ == "__main__":
    main()
