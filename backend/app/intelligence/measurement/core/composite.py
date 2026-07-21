from dataclasses import dataclass

from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.core.formula import DerivedMeasurementEngine
from app.intelligence.measurement.core.formula import FormulaDefinition


@dataclass(frozen=True)
class WeightedComponent:
    variable: str
    measurement_id: str
    weight: float


class WeightedCompositeEngine:

    def __init__(
        self,
    ):
        self._derived = DerivedMeasurementEngine()

    def compose(
        self,
        formula: FormulaDefinition,
        components: list[WeightedComponent],
        measurements: list[Measurement],
    ) -> Measurement:
        expression = " + ".join(
            f"({component.variable} * {component.weight})"
            for component in components
        )

        weighted_formula = FormulaDefinition(
            definition=formula.definition,
            expression=expression,
            variable_measurement_ids={
                component.variable: component.measurement_id
                for component in components
            },
            version=formula.version,
        )

        return self._derived.derive(
            weighted_formula,
            measurements,
        )


