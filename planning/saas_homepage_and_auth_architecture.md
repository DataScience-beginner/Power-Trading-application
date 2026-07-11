# Innowatt Energy AI Solutions — SaaS Wrapper and Auth Architecture

## Purpose

Innowatt Energy AI Solutions needs a public SaaS wrapper around the existing authenticated power trading dashboard.

The current application is the product workspace users see after login. The new wrapper introduces the enterprise-facing website, pricing, login entry, and role-aware product positioning without disturbing the existing dashboard.

## Product positioning

**Name:** Innowatt Energy AI Solutions

**Positioning:** AI-powered power procurement, scheduling, and trading intelligence for enterprise energy consumers.

**Core promise:** Help clients reduce power procurement cost by planning when to use Solar, IEX, and TNEB, while forecasting demand and future market opportunity.

## Recommended onboarding model

This is a B2B enterprise SaaS product, not pure B2C.

### Phase 1: Sales-led onboarding

- Client requests demo/contact.
- Innowatt admin creates the client account.
- Admin creates portfolios and initial users.
- Client logs in and sees only their workspace.
- Admin can toggle between all clients.

This is safest for early production because data models, energy contracts, portfolio structures, and report formats may differ by client.

### Phase 2: Assisted self-onboarding

- Client submits onboarding request.
- Admin approves workspace creation.
- Client uploads required documents.
- AI onboarding agent validates file structure and missing data.

### Phase 3: Agentic onboarding

- Email ingestion agent fetches client reports from mailbox.
- Parser agent validates DAM/RTM/GDAM/SCH/DOR files.
- Data quality agent flags gaps.
- Dashboard agent prepares client-specific analytics.
- Procurement agent generates shortfall and purchase recommendations.

## Public website routes

| Route | Purpose | Main question answered |
|---|---|---|
| `/` | Homepage | What is Innowatt and why should an enterprise care? |
| `/platform` | Platform overview | What capabilities does the product provide? |
| `/pricing` | Plans | How can a client buy/adopt it? |
| `/partners` | Partner ecosystem | Who can integrate or collaborate? |
| `/careers` | Hiring page | What kind of specialists are we building with? |
| `/contact` | Demo/contact | How does a client start? |
| `/login` | Login chooser | Am I an admin or client user? |
| `/app` | Authenticated workspace | Existing dashboard/product experience. |

## Authenticated workspace roles

### Admin

Admin users should be able to:

- view all clients;
- switch between clients;
- create/manage client accounts;
- create/manage portfolios;
- upload/manage client files;
- inspect database/data quality;
- run calculations;
- view dashboards and reports across clients.

### Client

Client users should be able to:

- see only their assigned client workspace;
- see only their portfolios;
- view dashboard, energy schedule, analytics, reports, and AI insights;
- upload files only if permissioned;
- view profile, contract, and onboarding status.

## Page/component plan

```text
frontend-react/src/
  App.tsx                         Route owner
  pages/
    AppShell.tsx                  Existing authenticated dashboard shell
    public/
      SaasHome.tsx                Homepage and public informational pages
      Login.tsx                   Role-aware login entry
      Pricing.tsx                 SaaS pricing and packaging
  layouts/
    PublicLayout.tsx              Public top nav/footer wrapper
```

## Implementation principles

- Keep public marketing pages separate from dashboard pages.
- Keep existing dashboard behavior intact.
- Use `/app` as the authenticated product entrypoint.
- Use `/login` as the role selector.
- Do not implement fully automatic B2C signup in phase 1.
- Do not expose production data publicly.
- Keep files under the QC target of 1,000 lines.

## Immediate scope

This pass creates the public SaaS wrapper and route structure. It does not yet implement full client-user authentication or client-level row security. Those should be implemented as a dedicated backend auth/data-scope milestone.

