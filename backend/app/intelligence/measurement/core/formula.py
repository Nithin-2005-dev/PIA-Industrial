import ast
from dataclasses import dataclass
from dataclasses import replace
from math import sqrt
from operator import add
from operator import mul
from operator import sub
from operator import truediv

from app.intelligence.measurement.domain import Measurement
from app.intelligence.measurement.domain import MeasurementDefinition
from app.intelligence.measurement.domain import MeasurementMethod
from app.intelligence.measurement.domain import MeasurementTrace
from app.intelligence.measurement.domain import MeasurementUncertainty
from app.intelligence.measurement.domain import MeasurementUnit
from app.intelligence.measurement.domain import NormalizationMethod
from app.intelligence.measurement.core.ids import stable_measurement_id


@dataclass(frozen=True)
class FormulaDefinition:
    definition: MeasurementDefinition
    expression: str
    variable_measurement_ids: dict[str, str]
    version: str = "1.0"


class DerivedMeasurementEngine:
    _OPERATORS = {
        ast.Add: add,
        ast.Sub: sub,
        ast.Mult: mul,
        ast.Div: truediv,
    }

    def derive(
        self,
        formula: FormulaDefinition,
        measurements: list[Measurement],
    ) -> Measurement:
        by_id = {
            measurement.id: measurement
            for measurement in measurements
        }

        values = {}

        for variable, measurement_id in (
            formula.variable_measurement_ids.items()
        ):
            values[variable] = by_id[
                measurement_id
            ].value

        value = self._evaluate(
            formula.expression,
            values,
        )

        dependencies = tuple(
            formula.variable_measurement_ids.values()
        )

        first = by_id[
            dependencies[0]
        ]

        uncertainty_width = self._propagated_uncertainty_width(
            formula,
            by_id,
            values,
        )

        confidence = min(
            by_id[dependency_id].confidence
            for dependency_id in dependencies
        )

        return Measurement(
            id=stable_measurement_id(
                formula.definition.id,
                formula.version,
                *dependencies,
            ),
            definition=formula.definition,
            unit=formula.definition.unit,
            value=value,
            confidence=confidence,
            uncertainty=MeasurementUncertainty(
                lower_bound=value - uncertainty_width,
                upper_bound=value + uncertainty_width,
                variance=uncertainty_width * uncertainty_width,
                method="finite_difference_error_propagation",
            ),
            quality_score=min(
                by_id[dependency_id].quality_score
                for dependency_id in dependencies
            ),
            measurement_method=MeasurementMethod(
                name="derived_formula",
                version=formula.version,
                algorithm="safe_ast_arithmetic",
                parameters={
                    "expression": formula.expression,
                },
            ),
            normalization_method=NormalizationMethod(
                name="formula_native_unit",
                version="1.0",
                source_unit=formula.definition.unit,
                target_unit=formula.definition.unit,
            ),
            provenance=replace(
                first.provenance,
                transformations=(
                    *first.provenance.transformations,
                    "derived_formula",
                ),
            ),
            timestamp=first.timestamp,
            version=formula.version,
            traceability=MeasurementTrace(
                pipeline_version=(
                    first.traceability.pipeline_version
                ),
                dependency_ids=dependencies,
                formula=formula.expression,
                evaluator="derived_formula",
            ),
            dependencies=dependencies,
            validation_status=first.validation_status,
            metadata={
                "propagation": "finite_difference",
            },
        )

    def _propagated_uncertainty_width(
        self,
        formula: FormulaDefinition,
        by_id: dict[str, Measurement],
        values: dict[str, float],
    ) -> float:
        propagated_variance = 0.0

        for variable, measurement_id in (
            formula.variable_measurement_ids.items()
        ):
            measurement = by_id[
                measurement_id
            ]

            width = (
                measurement.uncertainty.upper_bound
                - measurement.uncertainty.lower_bound
            ) / 2.0

            if width <= 0:
                continue

            high_values = dict(
                values
            )
            low_values = dict(
                values
            )

            high_values[
                variable
            ] = values[variable] + width
            low_values[
                variable
            ] = values[variable] - width

            high = self._evaluate(
                formula.expression,
                high_values,
            )
            low = self._evaluate(
                formula.expression,
                low_values,
            )

            sensitivity = (
                high - low
            ) / (2.0 * width)

            propagated_variance += (
                sensitivity
                * sensitivity
                * measurement.uncertainty.variance
            )

        return sqrt(
            propagated_variance
        )

    def _evaluate(
        self,
        expression: str,
        values: dict[str, float],
    ) -> float:
        tree = ast.parse(
            expression,
            mode="eval",
        )

        return float(
            self._node(
                tree.body,
                values,
            )
        )

    def _node(
        self,
        node,
        values: dict[str, float],
    ) -> float:
        if isinstance(
            node,
            ast.Constant,
        ) and isinstance(
            node.value,
            int | float,
        ):
            return float(
                node.value
            )

        if isinstance(
            node,
            ast.Name,
        ):
            return float(
                values[
                    node.id
                ]
            )

        if isinstance(
            node,
            ast.BinOp,
        ):
            operator = self._OPERATORS[
                type(node.op)
            ]

            return operator(
                self._node(
                    node.left,
                    values,
                ),
                self._node(
                    node.right,
                    values,
                ),
            )

        raise ValueError(
            "unsupported formula expression"
        )


