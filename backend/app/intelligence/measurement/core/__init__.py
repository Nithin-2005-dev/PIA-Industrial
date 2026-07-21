from importlib import import_module

_EXPORTS = {
    "ActiveMeasurementService": "app.intelligence.measurement.core.active",
    "CostBasedMeasurementOptimizer": "app.intelligence.measurement.core.execution",
    "EnterpriseAccuracyPipeline": "app.intelligence.measurement.core.accuracy",
    "MeasurementCache": "app.intelligence.measurement.core.store",
    "MeasurementComputationNode": "app.intelligence.measurement.core.execution",
    "MeasurementDependencyGraph": "app.intelligence.measurement.core.recompute",
    "MeasurementEngine": "app.intelligence.measurement.core.engine",
    "MeasurementExecutionPlanner": "app.intelligence.measurement.core.execution",
    "MeasurementExecutor": "app.intelligence.measurement.core.execution",
    "NormalizationPipeline": "app.intelligence.measurement.core.normalization_pipeline",
    "StreamingMeasurementEngine": "app.intelligence.measurement.core.streaming",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

