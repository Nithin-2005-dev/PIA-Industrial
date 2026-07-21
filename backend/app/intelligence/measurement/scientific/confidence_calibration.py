from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceObservation:
    measurement_id: str
    predicted_confidence: float
    observed_success: bool


@dataclass(frozen=True)
class ConfidenceCalibrationReport:
    measurement_id: str
    predicted_confidence: float
    observed_reliability: float
    calibration_error: float
    sample_size: int


class ConfidenceCalibrationModel:

    def calibrate(
        self,
        measurement_id: str,
        predicted_confidence: float,
        observations: list[ConfidenceObservation],
    ) -> ConfidenceCalibrationReport:
        relevant = [
            observation
            for observation in observations
            if observation.measurement_id == measurement_id
        ]

        if not relevant:
            return ConfidenceCalibrationReport(
                measurement_id=measurement_id,
                predicted_confidence=predicted_confidence,
                observed_reliability=predicted_confidence,
                calibration_error=0.0,
                sample_size=0,
            )

        observed = sum(
            1
            for observation in relevant
            if observation.observed_success
        ) / len(
            relevant
        )

        return ConfidenceCalibrationReport(
            measurement_id=measurement_id,
            predicted_confidence=predicted_confidence,
            observed_reliability=observed,
            calibration_error=abs(
                predicted_confidence - observed
            ),
            sample_size=len(
                relevant
            ),
        )

    def adjusted_confidence(
        self,
        report: ConfidenceCalibrationReport,
    ) -> float:
        if report.sample_size == 0:
            return report.predicted_confidence

        return max(
            0.0,
            min(
                1.0,
                (
                    report.predicted_confidence
                    + report.observed_reliability
                )
                / 2.0,
            ),
        )

import math
from typing import List, Dict, Any

class ECECalibrationEngine:
    def __init__(self, num_bins: int = 10):
        self.num_bins = num_bins

    def calculate_ece(self, predictions: List[Any]) -> float:
        """
        Calculates True Expected Calibration Error (ECE) by bucketing 
        predictions into confidence intervals.
        """
        if not predictions:
            return 0.0
            
        # Initialize bins (e.g., 0.0-0.1, 0.1-0.2...)
        bins = {i: {'confidences': [], 'accuracies': []} for i in range(self.num_bins)}
        
        for p in predictions:
            # Map confidence (0.0 to 1.0) to a bin index
            bin_idx = min(int(p.predicted_confidence * self.num_bins), self.num_bins - 1)
            bins[bin_idx]['confidences'].append(p.predicted_confidence)
            # Assume p.actual_is_correct is a boolean flag based on historical truth
            bins[bin_idx]['accuracies'].append(1.0 if getattr(p, 'actual_is_correct', False) else 0.0)
            
        ece = 0.0
        total_samples = len(predictions)
        
        for b in bins.values():
            bin_size = len(b['confidences'])
            if bin_size == 0:
                continue
                
            avg_confidence = sum(b['confidences']) / bin_size
            avg_accuracy = sum(b['accuracies']) / bin_size
            
            # Weight the bin's error by its proportion of the total sample
            weight = bin_size / total_samples
            ece += weight * abs(avg_confidence - avg_accuracy)
            
        return ece

    def calibrate_confidence(self, raw_confidence: float, historical_ece: float) -> float:
        """
        Applies a penalty map to raw confidence based on the adapter's historical ECE.
        (A simplified Platt scaling heuristic).
        """
        # If ECE is 0 (perfect), return raw. If ECE is high, regress toward uncertainty (0.5)
        penalty_factor = min(historical_ece * 2.0, 1.0) 
        calibrated = raw_confidence * (1.0 - penalty_factor) + 0.5 * penalty_factor
        return max(0.001, min(calibrated, 0.999))


