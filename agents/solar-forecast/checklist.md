# Solar Forecast Checklist

- JWT tenant and portfolio authorization passed.
- Latitude, longitude, capacity, and horizon validated.
- Historical observations identify actual/synthetic status and version.
- Weather provider, source, and fallback status recorded.
- Training and holdout periods are time ordered.
- MAE, MAPE, and holdout count reported where history permits.
- P10 is below P50 and P50 is below P90.
- Model, contract, inputs, confidence, limitations, and audit event persisted.
- No market or schedule mutation occurred.
