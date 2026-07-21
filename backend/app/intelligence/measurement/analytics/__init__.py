from importlib import import_module

_EXPORTS = {
    "DriftDetectionEngine": "app.intelligence.measurement.analytics.drift",
    "DriftResult": "app.intelligence.measurement.analytics.drift",
    "GraphMeasurementEngine": "app.intelligence.measurement.analytics.graph",
    "GraphMeasurementResult": "app.intelligence.measurement.analytics.graph",
    "OutlierDetectionEngine": "app.intelligence.measurement.analytics.outliers",
    "StatisticalEngine": "app.intelligence.measurement.analytics.statistical",
    "StatisticalReport": "app.intelligence.measurement.analytics.statistical_pipeline",
    "StatisticsPipeline": "app.intelligence.measurement.analytics.statistical_pipeline",
    "TimeSeriesMeasurementEngine": "app.intelligence.measurement.analytics.time_series",
    "TrendEstimate": "app.intelligence.measurement.analytics.time_series",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

