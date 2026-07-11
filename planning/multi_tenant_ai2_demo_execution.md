# Multi-Tenant AI-2 Demo Execution

## Delivered scope

- Five idempotent synthetic demo clients with two or more portfolios.
- Platform-admin visibility across tenants and JWT client-user isolation.
- Synthetic generation and compact trading histories clearly labelled as demo data.
- Coordinate-aware solar forecasting with Open-Meteo, deterministic fallback, calibration, P10/P50/P90, and backtesting.
- Forecast persistence, audit records, endpoint registry metadata, responsive UI, and chatbot explanation.

## Demo acceptance

1. Provision from AI Predict as platform admin with a temporary shared demo password.
2. Confirm admin `/api/clients` returns five demo tenants (plus any intentionally retained non-demo tenant).
3. Sign in as `client1@demo.innowattenergy.com`; confirm only one client and its portfolios appear.
4. Run a seven-day solar forecast and inspect source classification, weather source, confidence, MAPE, and limitations.
5. Ask the chatbot to explain the latest solar forecast.
6. Confirm a client token cannot read or run another tenant's forecast.

## Next model promotions

- Ingest actual inverter/meter generation at 15-minute resolution.
- Add weather-history feature materialization and missing-data policies.
- Benchmark persistence, seasonal-naive, gradient boosting, and quantile models.
- Promote a champion only after rolling-origin backtests beat the physical baseline by approved thresholds.
- Add demand and next-day IEX forecast families before procurement optimization.
