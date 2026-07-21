import yaml
from pathlib import Path
from pydantic import BaseModel, Field

class HardThresholds(BaseModel):
    overall_score_min: int = 90
    graph_validation_required: bool = True
    deterministic_assertions_required: bool = True

class SoftThresholds(BaseModel):
    presentation_score_min: int = 89
    performance_regression_max_percent: int = 10

class CIThresholds(BaseModel):
    hard: HardThresholds
    soft: SoftThresholds

class PerformancePolicy(BaseModel):
    planner_ms: int
    graph_ms: int
    reasoning_ms: int
    presentation_ms: int

class DatasetConfig(BaseModel):
    repository: str
    commit_sha: str
    snapshots_dir: str
    size: str

class BenchmarkManifest(BaseModel):
    version: str
    dataset: DatasetConfig
    performance_policy: PerformancePolicy
    ci_thresholds: CIThresholds
    enabled_suites: list[str]
    providers: list[str]

    @classmethod
    def load(cls, path: str | Path) -> "BenchmarkManifest":
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)
