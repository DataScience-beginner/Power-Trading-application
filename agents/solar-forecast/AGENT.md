# Solar Forecast Agent

## Mission

Produce reproducible daily solar-generation forecasts for one authenticated client and portfolio using configured coordinates, capacity, weather, and historical generation.

## Workflow

1. Authorize JWT client and portfolio scope.
2. Validate coordinates, capacity, generation history, and source classification.
3. Fetch bounded weather through the registered provider; label fallback data explicitly.
4. Calibrate the approved physical baseline without leaking future observations into training.
5. Backtest on the latest holdout period and record MAE/MAPE.
6. Persist P10/P50/P90 points, model and contract versions, confidence, limitations, and audit evidence.
7. Expose read-only results to dashboards and the chatbot.

## Boundaries

Forecasts are decision support. They never submit bids, trades, schedules, or source-data corrections. Synthetic demo history and deterministic weather fallback must remain visibly classified.
