import datetime
import warnings
from typing import List, Tuple, Optional
from dataclasses import dataclass

from app.intelligence.measurement.domain.calendars import ICalendarProvider, StandardBusinessCalendar


@dataclass(frozen=True)
class TrendEstimate:
    slope: float
    intercept: float
    direction: str


class TimeSeriesMeasurementEngine:
    def __init__(self, calendar_provider: Optional[ICalendarProvider] = None):
        # Default to standard if no specific calendar is provided
        self.calendar = calendar_provider or StandardBusinessCalendar()

    def moving_average(
        self,
        values: list[float],
        window: int,
    ) -> list[float]:
        """Legacy moving average method. Pending deprecation."""
        warnings.warn("moving_average is deprecated. Use ewma instead to prevent lag.", DeprecationWarning)
        if window <= 0:
            raise ValueError(
                "window must be positive"
            )

        result = []

        for index in range(
            len(values)
        ):
            start = max(
                0,
                index - window + 1,
            )
            segment = values[
                start : index + 1
            ]
            result.append(
                sum(segment)
                / len(segment)
            )

        return result

    def ewma(self, values: List[float], alpha: float = 0.3) -> List[float]:
        """
        Calculates the Exponentially Weighted Moving Average (EWMA).
        Equation: S_t = α * Y_t + (1 - α) * S_{t-1}
        """
        if not values:
            return []
            
        ewma_series = [values[0]]
        for i in range(1, len(values)):
            ewma_val = (alpha * values[i]) + ((1 - alpha) * ewma_series[-1])
            ewma_series.append(ewma_val)
            
        return ewma_series

    def normalize_to_business_days(
        self, 
        time_series: List[Tuple[datetime.date, float]],
        entity_id: Optional[str] = None
    ) -> List[Tuple[datetime.date, float]]:
        """
        Rolls non-working day activity into the next available working day.
        Requires chronological sorting before processing.
        """
        if not time_series:
            return []

        normalized = []
        off_day_accumulator = 0.0
        
        # Ensure chronological order
        sorted_series = sorted(time_series, key=lambda x: x[0])
        
        for dt, value in sorted_series:
            if not self.calendar.is_working_day(dt, entity_id): 
                # Accumulate the work done on the off-day
                off_day_accumulator += value
            else:
                # Add the accumulated work to the current working day
                adjusted_value = value + off_day_accumulator
                off_day_accumulator = 0.0
                normalized.append((dt, adjusted_value))
                
        # Edge Case: Trailing off-days (e.g., series ends on a Sunday)
        # Search forward to find the next valid working day to deposit the accumulator
        if off_day_accumulator > 0.0 and sorted_series:
            last_dt = sorted_series[-1][0]
            next_day = last_dt + datetime.timedelta(days=1)
            # Find the next working day to assign the trailing accumulated value
            while not self.calendar.is_working_day(next_day, entity_id):
                next_day += datetime.timedelta(days=1)
            normalized.append((next_day, off_day_accumulator))
            
        return normalized

    def trend(
        self,
        values: list[float],
    ) -> TrendEstimate:
        count = len(
            values
        )

        if count < 2:
            return TrendEstimate(
                slope=0.0,
                intercept=values[0] if values else 0.0,
                direction="flat",
            )

        xs = list(
            range(count)
        )
        x_mean = sum(xs) / count
        y_mean = sum(values) / count

        denominator = sum(
            (
                x - x_mean
            )
            ** 2
            for x in xs
        )

        if denominator == 0:
            slope = 0.0
        else:
            slope = sum(
                (
                    xs[index]
                    - x_mean
                )
                * (
                    values[index]
                    - y_mean
                )
                for index in range(count)
            ) / denominator

        intercept = y_mean - slope * x_mean

        direction = "flat"

        if slope > 0:
            direction = "up"
        elif slope < 0:
            direction = "down"

        return TrendEstimate(
            slope=slope,
            intercept=intercept,
            direction=direction,
        )


