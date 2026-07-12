# Deployment Governance Memory

- Railway project currently uses `production`, `development`, and `staging` environments.
- DEV application service: `power-trading-app-dev` on `develop`.
- TEST application service: `power-trading-app-staging` on `staging`.
- Existing production service remains `power-trading-app`.
- Never store Railway tokens, database URLs, or API keys in this file.
