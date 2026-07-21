# Forecasting Package (The Trend Predictor)

This package contains the logic for **Forecasting**. It takes historical data (like how fast bugs are being fixed over the last year) and predicts where the line is going next month.

## `engine.py` (The Weatherman)
- **What it does**: The main script that takes historical data and asks the mathematical models to predict the future. 
- **Analogy**: Like a weatherman taking historical temperature data to predict tomorrow's weather.

## `baseline_models.py` (The Mathematical Brains)
- **What it does**: Contains the actual statistical math formulas used to predict the future (e.g., Linear Regression, Exponential Smoothing).
- **Why we need it**: The AI shouldn't just guess the future; it should use rigorous statistics to draw trend lines.

## `factory.py` (The Model Selector)
- **What it does**: Not all data can be predicted the same way. The factory looks at the data and decides *which* mathematical brain to use. (e.g., "This data looks like a straight line, let's use the Linear model").

## `models.py` (The Dictionary)
- **What it does**: Defines the strict data structures for what a "Forecast" looks like in code. Ensures every forecast has a "Predicted Value" and a "Margin of Error."

## `validation.py` (The Accuracy Checker)
- **What it does**: Before showing a forecast to a user, this script tests how accurate the model is. It does this by asking the model to predict *yesterday* based on *last week*. If it gets *yesterday* wrong, we throw the model out.
- **Why we need it**: To prevent wild, wildly inaccurate predictions from breaking the system.
