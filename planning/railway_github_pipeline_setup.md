# Railway and GitHub Pipeline Setup

The repository workflows are committed under `.github/workflows/`. The following provider settings are required once in GitHub and Railway.

## GitHub repository settings

Create these GitHub deployment environments:

| Environment | Allowed branches | Required reviewer |
|---|---|---|
| `development` | `develop` | none |
| `staging` | `staging` | none |
| `production` | `V2` | Cofounder |

Configure branch protection or rulesets:

### `develop`

- Require pull requests.
- Require the `Quality Gate / Golden rigorous quality gate` check.
- Require the `Security and Supply Chain Gate / Secret and dependency checks` check.
- Block force pushes and branch deletion.

### `staging`

- Require pull requests unless the `innowatt-release-bot` promotion is explicitly allowed.
- Require the same quality and security checks.
- Block force pushes and branch deletion.

### `V2`

- Require pull requests from `staging`.
- Require at least one reviewer.
- Require quality and security checks.
- Block force pushes and branch deletion.
- Prevent administrators from bypassing rules except for a documented incident.

GitHub may restrict required reviewers and environment secrets on private repositories according to the repository plan. Confirm plan capability before relying on the production approval gate.

## Railway settings

For each application service, configure automatic deployment from the matching branch:

| Railway environment | Service | Branch |
|---|---|---|
| development | `power-trading-app-dev` | `develop` |
| staging | `power-trading-app-staging` | `staging` |
| production | `power-trading-app` | `V2` |

Enable Railway `Wait for CI` on all three application services. This prevents Railway from deploying a GitHub-connected commit until the required workflow checks complete. Railway must remain the deployment executor; GitHub Actions is the quality and approval controller.

## Secrets

Do not put Railway or application secrets in this repository.

Railway owns runtime secrets such as `DATABASE_URL`, `JWT_SECRET_KEY`, `AI_FOUNDATION_API_KEY`, SMTP credentials, and provider tokens. GitHub Actions should not receive production database credentials. If a future workflow needs Railway API access, use a project-scoped token stored as an environment secret and expose it only to the approved deployment job.

## Promotion behavior

- Merge to `develop`: Railway DEV deploys after CI.
- Successful `Quality Gate` on `develop`: `promote_staging.yml` pushes the exact tested SHA to `staging`.
- Push/merge to `staging`: Railway TEST deploys after CI.
- Pull request `staging` → `V2`: cofounder reviews the release.
- Push to `V2`: `production_release.yml` waits for the protected `production` approval; Railway PROD then deploys after CI.

## First operational test

After provider settings are configured, use a harmless documentation-only pull request to verify:

1. Pull-request checks run.
2. Merge to `develop` deploys DEV.
3. The exact commit is promoted to `staging`.
4. TEST deploys and checks complete.
5. The production workflow pauses for the cofounder and does not deploy without approval.
