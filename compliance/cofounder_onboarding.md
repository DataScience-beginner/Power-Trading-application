# Cofounder GitHub and Production Approval Onboarding

## Account setup

The cofounder should:

1. Create or use a GitHub account tied to the approved business email address.
2. Enable two-factor authentication.
3. Accept the repository invitation.
4. Use an individual account; never share another person’s credentials.
5. Confirm that the account can view pull requests and deployment reviews.

The account creation and email verification must be completed by the cofounder. An agent must not create or impersonate that identity.

## Repository access

Grant the minimum required repository role. The cofounder needs review access to `staging` → `V2` pull requests and approval access to the GitHub `production` environment. They do not need Railway database credentials.

## Production environment configuration

In GitHub repository Settings → Environments:

1. Create or open the `production` environment.
2. Add the cofounder as a required reviewer.
3. Prevent self-review where available.
4. Restrict deployment branches to `V2`.
5. Keep production secrets out of repository-level secrets.

The `production_release.yml` workflow will pause until the required reviewer approves the deployment job.

## Safe validation before onboarding

Use `.github/workflows/release_candidate.yml` with `source_branch=staging`. It runs the rigorous suite with synthetic data and creates explicit evidence with:

```text
approval_mode=mock-data-validation
production_deploy=false
```

This validates the workflow and evidence format without pretending that a mock approval is a real production authorization.

## First real release

After onboarding:

1. Cofounder reviews the `staging` → `V2` pull request.
2. CI and security checks pass.
3. Production backup is confirmed.
4. Cofounder approves the GitHub `production` deployment.
5. Railway deploys the exact approved `V2` commit.
6. Post-deployment health and smoke results are recorded.
