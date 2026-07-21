from typing import Protocol
from .models import CalibrationProfile, CalibrationResult


class CalibrationStrategy(Protocol):
    """Protocol for calibration strategies."""
    def calibrate(self, value: float, profile: CalibrationProfile) -> CalibrationResult:
        ...


class MeanStdStrategy:
    """Z-score based calibration using Mean and Standard Deviation."""
    
    def calibrate(self, value: float, profile: CalibrationProfile) -> CalibrationResult:
        z_score = (value - profile.mean) / profile.stddev if profile.stddev > 0 else 0.0
        return CalibrationResult(
            raw_value=value,
            normalized=z_score,
            z_score=z_score,
            percentile=None,
            robust_z=None,
            baseline=profile,
            method="mean_std"
        )


class MedianMADStrategy:
    """Robust Z-score calibration using Median and Median Absolute Deviation (MAD)."""
    
    def calibrate(self, value: float, profile: CalibrationProfile) -> CalibrationResult:
        # 1.4826 is the scaling factor for normal distribution consistency
        mad = profile.mad
        robust_z = (value - profile.median) / (1.4826 * mad) if mad > 0 else 0.0
        return CalibrationResult(
            raw_value=value,
            normalized=robust_z,
            z_score=None,
            percentile=None,
            robust_z=robust_z,
            baseline=profile,
            method="median_mad"
        )


class PercentileStrategy:
    """Percentile-based calibration."""
    
    def calibrate(self, value: float, profile: CalibrationProfile) -> CalibrationResult:
        closest_p = 0
        for p, p_val in sorted(profile.percentiles.items()):
            if value >= p_val:
                closest_p = p
        
        return CalibrationResult(
            raw_value=value,
            normalized=closest_p / 100.0,
            z_score=None,
            percentile=float(closest_p),
            robust_z=None,
            baseline=profile,
            method="percentile"
        )
