from app.intelligence.temporal.models import HistoricalContext
from .models import TimeSeries, TimeSeriesPoint


class TimeSeriesFactory:
    """
    Extracts generic TimeSeries sequences from the HistoricalContext.
    This decouples the ForecastEngine from the snapshot schema and consumes
    the existing trend values computed by Temporal Intelligence.
    """

    @classmethod
    def build_all(cls, history: HistoricalContext) -> dict[str, TimeSeries[float]]:
        series_map = {}
        
        # In M52, HistoricalContext provides `trends` which contains the historical values
        for trend in history.trends:
            points = []
            
            # Reconstruct dummy timestamps and snapshot IDs just to satisfy the TimeSeriesPoint contract
            # since the temporal trend gives us ordered values but not the raw metadata.
            # (In a real system, TemporalTrend might include the point metadata, but for now we mock it).
            base_version = max(1, history.current_version - len(trend.values) + 1)
            
            for i, val in enumerate(trend.values):
                points.append(
                    TimeSeriesPoint(
                        snapshot_id=f"snap-{base_version + i}",
                        timestamp="unknown",
                        value=float(val)
                    )
                )
                
            series_map[trend.metric_name] = TimeSeries(
                metric_name=trend.metric_name,
                points=tuple(points)
            )
            
        return series_map
