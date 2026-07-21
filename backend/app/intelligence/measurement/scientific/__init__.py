from importlib import import_module

_EXPORTS = {
    "AccuracyProfileRegistry": "app.intelligence.measurement.scientific.accuracy_profiles",
    "CatalogValidationService": "app.intelligence.measurement.scientific.scientific_validation",
    "ConfidenceCalibrationModel": "app.intelligence.measurement.scientific.confidence_calibration",
    "ConfidenceCalibrationReport": "app.intelligence.measurement.scientific.confidence_calibration",
    "ConfidenceObservation": "app.intelligence.measurement.scientific.confidence_calibration",
    "EnterpriseMeasurementCatalog": "app.intelligence.measurement.scientific.scientific_catalog",
    "ExpectedMeasurement": "app.intelligence.measurement.scientific.test_corpus",
    "MeasurementAccuracyProfile": "app.intelligence.measurement.scientific.accuracy_profiles",
    "MeasurementTestCorpus": "app.intelligence.measurement.scientific.test_corpus",
    "MeasurementTestDataset": "app.intelligence.measurement.scientific.test_corpus",
    "ScientificMeasurementApi": "app.intelligence.measurement.scientific.scientific_api",
    "ScientificMeasurementSpec": "app.intelligence.measurement.scientific.scientific_catalog",
    "ScientificValidationEngine": "app.intelligence.measurement.scientific.scientific_validation",
    "ScientificValidationReport": "app.intelligence.measurement.scientific.scientific_validation",
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value

