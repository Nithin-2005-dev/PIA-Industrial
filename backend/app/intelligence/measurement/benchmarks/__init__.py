from importlib import import_module

_EXPORTS = {
    "BenchmarkDataset": "app.intelligence.measurement.benchmarks.benchmark_datasets",
    "BenchmarkDatasetRegistry": "app.intelligence.measurement.benchmarks.benchmark_datasets",
    "BenchmarkEngine": "app.intelligence.measurement.benchmarks.benchmark",
    "BenchmarkResult": "app.intelligence.measurement.benchmarks.benchmark",
    "BenchmarkScope": "app.intelligence.measurement.benchmarks.benchmark_datasets",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

