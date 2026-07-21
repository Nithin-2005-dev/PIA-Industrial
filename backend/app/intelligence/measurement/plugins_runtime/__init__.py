from importlib import import_module

_EXPORTS = {
    "MeasurementMarketplace": "app.intelligence.measurement.plugins_runtime.packs",
    "MeasurementPack": "app.intelligence.measurement.plugins_runtime.packs",
    "MeasurementPluginRegistry": "app.intelligence.measurement.plugins_runtime.plugins",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

