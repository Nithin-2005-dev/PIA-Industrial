# Production Update: Measurement Mathematical Hardening (Sparsity & Smoothing)

## Overview
This update resolves two critical mathematical distortions in the Measurement Layer related to how we calculate metrics (such as developer velocity and subsystem activity). It introduces strict dependency injection for calendars to handle sparsity and updates time-series calculations to smooth outliers without causing metric lag.

## Key Changes

### 1. The "Off-Day Sparsity" Fix
Naive metric calculations were causing false "productivity drops" on weekends or PTO days because activity was simply missing from those dates.
- **Implementation**: Created a strict `ICalendarProvider` protocol in `app/measurement/domain/calendars.py`.
- **Implementation**: Implemented `StandardBusinessCalendar` as a fallback, filtering out weekends.
- **Algorithm Update**: Added `normalize_to_business_days` in `TimeSeriesMeasurementEngine`, which rolls non-working day activity into the next available working day via a chronological accumulator, effectively neutralizing weekend drop-offs.
- **Architectural Constraint**: Preserved purity and determinism by ensuring no external network calls (e.g., Workday or Google Calendar APIs) are made. Future extensions will use an internal DB-backed `DatabaseCalendarProvider`.

### 2. The "Ghost Outlier" Fix
Previous calculations relied on lagging moving averages which failed to respond smoothly to recent data points.
- **Implementation**: Replaced `moving_average` logic with standard Exponentially Weighted Moving Average (`ewma`) in `app/measurement/analytics/time_series.py`.
- **Algorithm Update**: `S_t = α * Y_t + (1 - α) * S_{t-1}` allows for faster response times without extreme outlier spiking.
- **Deprecation**: The legacy `moving_average` method was wrapped in a `DeprecationWarning` rather than deleted, allowing the system to continue compiling while callers are safely migrated to `ewma`.
