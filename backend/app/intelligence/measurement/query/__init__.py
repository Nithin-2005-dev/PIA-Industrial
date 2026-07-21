from importlib import import_module

_EXPORTS = {
    "MeasurementExplainer": "app.intelligence.measurement.query.lineage",
    "MeasurementLineageGraph": "app.intelligence.measurement.query.lineage",
    "MeasurementLineageQueryEngine": "app.intelligence.measurement.query.lineage_query",
    "MeasurementLineageService": "app.intelligence.measurement.query.lineage",
    "MqlEngine": "app.intelligence.measurement.query.mql",
    "MqlParser": "app.intelligence.measurement.query.mql",
    "MqlQuery": "app.intelligence.measurement.query.mql",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

