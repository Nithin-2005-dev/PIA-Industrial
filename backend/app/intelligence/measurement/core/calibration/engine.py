import statistics
from collections import defaultdict
from typing import Sequence
from dataclasses import replace

from app.intelligence.measurement.domain import Measurement
from .models import CalibrationProfile, CalibrationResult
from .strategies import MeanStdStrategy, MedianMADStrategy, PercentileStrategy


class StatisticalCalibrationEngine:
    """Computes statistical baselines and calibrates measurements."""
    
    def calibrate(self, measurements: Sequence[Measurement]) -> Sequence[Measurement]:
        """Group measurements by definition, compute profiles, and calibrate."""
        if not measurements:
            return measurements
            
        grouped = defaultdict(list)
        for m in measurements:
            grouped[m.definition.id].append(m)
            
        profiles = {}
        for def_id, group in grouped.items():
            values = [m.value for m in group]
            profiles[def_id] = self._build_profile(values)
            
        calibrated_measurements = []
        for m in measurements:
            profile = profiles[m.definition.id]
            
            mean_std = MeanStdStrategy().calibrate(m.value, profile)
            median_mad = MedianMADStrategy().calibrate(m.value, profile)
            percentile = PercentileStrategy().calibrate(m.value, profile)
            
            # Recommendation: if sample size < 30 use Median + MAD, else Mean + StdDev
            if profile.sample_size < 30:
                primary_normalized = median_mad.normalized
                primary_method = median_mad.method
            else:
                primary_normalized = mean_std.normalized
                primary_method = mean_std.method
                
            calibration = CalibrationResult(
                raw_value=m.value,
                normalized=primary_normalized,
                z_score=mean_std.z_score,
                percentile=percentile.percentile,
                robust_z=median_mad.robust_z,
                baseline=profile,
                method=primary_method
            )
            
            calibrated_m = replace(m, calibration=calibration)
            calibrated_measurements.append(calibrated_m)
            
        return calibrated_measurements

    def _build_profile(self, values: list[float]) -> CalibrationProfile:
        n = len(values)
        if n == 0:
            return CalibrationProfile(
                mean=0.0, median=0.0, stddev=0.0, mad=0.0,
                min_value=0.0, max_value=0.0, percentiles={},
                sample_size=0, distribution="empty", confidence=0.0
            )
            
        mean = statistics.mean(values)
        median = statistics.median(values)
        
        try:
            stddev = statistics.stdev(values) if n > 1 else 0.0
        except statistics.StatisticsError:
            stddev = 0.0
            
        try:
            mad = statistics.median([abs(v - median) for v in values])
        except statistics.StatisticsError:
            mad = 0.0
            
        percentiles = {}
        if n > 0:
            sorted_v = sorted(values)
            for p in [10, 25, 50, 75, 90, 95, 99]:
                idx = int((p / 100.0) * (n - 1))
                percentiles[p] = sorted_v[idx]
                
        return CalibrationProfile(
            mean=mean,
            median=median,
            stddev=stddev,
            mad=mad,
            min_value=min(values),
            max_value=max(values),
            percentiles=percentiles,
            sample_size=n,
            distribution="skewed" if mad > 0 and abs(mean - median) / mad > 1.0 else "normal",
            confidence=min(1.0, n / 30.0)
        )
