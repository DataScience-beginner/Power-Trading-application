# Client And Data Model Architecture

## Purpose

This document explains the top-to-bottom client data model for the Power Trading application.

It separates the current implemented database model from the proposed planning/optimization model needed for solar banking, IEX forecasting, and procurement recommendations.

## Top-Level Business Hierarchy

```text
Client
  ├─ Monthly Solar Bank
  └─ Portfolios
       └─ Trading Day
            ├─ Uploaded Reports
            │    ├─ DOR-GDAM
            │    ├─ DOR-DAM
            │    ├─ DOR-RTM
            │    ├─ SCH-GDAM
            │    ├─ SCH-DAM
            │    └─ SCH-RTM
            │
            ├─ Time-Slot Transactions
            │    └─ 96 time blocks per uploaded report
            │
            ├─ Energy Schedule Calculation
            │    ├─ DOR market summaries
            │    ├─ SCH consumption after losses
            │    └─ Daily cost / savings metrics
            │
            └─ Procurement Planning
                 ├─ Demand forecast
                 ├─ IEX price forecast
                 ├─ Solar usage decision
                 ├─ IEX buy quantity
                 └─ TNEB/Grid fallback
```

## Current Implemented Database Model

The current ORM model has these main tables:

```text
clients
└─ portfolios
   ├─ daily_files
   │  └─ transactions
   │
   ├─ monthly_calculations
   │
   └─ energy_schedule_months
      └─ energy_schedule_days
```

### `clients`

Stores the client/entity.

Examples:

- Mellbro Sugars Pvt
- Grasim Industries

Important fields:

- `entity_id`
- `entity_name`
- `lat`
- `lon`
- `capacity_kw`
- `farm_type`

### `portfolios`

Stores one or more portfolio codes under a client.

Examples:

- `NPT0027_KA0`
- `NPT0019_TN0`

Relationship:

```text
One client -> many portfolios
```

### `daily_files`

Stores metadata for every uploaded DOR/SCH file.

For one portfolio and one trading day, the complete expected file set is:

```text
DOR-GDAM
DOR-DAM
DOR-RTM
SCH-GDAM
SCH-DAM
SCH-RTM
```

Important fields:

- `portfolio_id`
- `trading_date`
- `delivery_date`
- `main_category`: `DOR` or `SCH`
- `sub_category`: `GDAM`, `DAM`, or `RTM`
- `report_type`: combined value like `DOR-GDAM`
- `summary`
- `charges`
- `file_metadata`

Relationship:

```text
One portfolio -> many daily files
```

### `transactions`

Stores the time-slot level rows parsed from uploaded reports.

Expected granularity:

```text
96 time slots per report
15-minute interval
```

Transaction types:

- `buy`
- `sell`
- `scheduling`

Relationship:

```text
One daily file -> many transactions
```

### `monthly_calculations`

Stores monthly/day-level calculated results for dashboard and reporting.

This table is more flexible and stores calculation output in JSON through `calculation_data`.

### `energy_schedule_months`

Stores one energy schedule container per portfolio/month.

Relationship:

```text
One portfolio -> many energy schedule months
```

### `energy_schedule_days`

Stores daily energy schedule calculations inside a monthly sheet.

Contains:

- GDAM/DAM/RTM DOR summary values
- SCH consumption after losses
- Total scheduled MWh
- CTU losses
- Energy savings
- Total cost
- Completion flags

Relationship:

```text
One energy schedule month -> many energy schedule days
```

## Current Data Flow

```text
Excel Upload
  └─ Parser
       ├─ DOR Parser
       └─ SCH Parser
            ↓
     Parsed Universal Data
            ↓
     daily_files
            ↓
     transactions
            ↓
     energy_schedule_months / energy_schedule_days
            ↓
     dashboard metrics
```

## Proposed Optimization Data Model

To support the real business goal, we should add a planning layer above the existing report upload layer.

The proposed model should include:

```text
clients
├─ solar_banks
│  └─ solar_bank_entries
│
├─ portfolios
│  ├─ demand_forecasts
│  ├─ iex_price_forecasts
│  ├─ procurement_plans
│  └─ procurement_plan_timeslots
│
└─ optimization_results
```

### Proposed: `solar_banks`

Client-level monthly solar balance.

Why client-level:

```text
Solar is common for the client, not owned separately by each portfolio.
```

Possible fields:

- `client_id`
- `year`
- `month`
- `opening_solar_mwh`
- `consumed_solar_mwh`
- `remaining_solar_mwh`
- `expires_on`
- `status`

### Proposed: `solar_bank_entries`

Daily movement of solar balance.

Possible fields:

- `solar_bank_id`
- `date`
- `portfolio_id`
- `allocated_mwh`
- `consumed_mwh`
- `expired_mwh`
- `reason`

### Proposed: `demand_forecasts`

Portfolio/day forecast for consumption.

Possible fields:

- `portfolio_id`
- `forecast_date`
- `total_forecast_mwh`
- `day_forecast_mwh`
- `night_forecast_mwh`
- `timeslot_forecast`
- `model_version`

### Proposed: `iex_price_forecasts`

Forecasted IEX market price by date and market.

Possible fields:

- `forecast_date`
- `market`: `GDAM`, `DAM`, or `RTM`
- `average_price`
- `timeslot_prices`
- `confidence_score`
- `model_version`

### Proposed: `procurement_plans`

Daily recommendation generated by the optimization engine.

Possible fields:

- `client_id`
- `portfolio_id`
- `plan_date`
- `solar_available_mwh`
- `recommended_solar_mwh`
- `recommended_iex_mwh`
- `expected_tneb_mwh`
- `expected_cost`
- `expected_savings`
- `risk_level`
- `status`

### Proposed: `procurement_plan_timeslots`

96 time-slot detail for the daily recommendation.

Possible fields:

- `procurement_plan_id`
- `time_slot`
- `forecast_demand_mw`
- `recommended_solar_mw`
- `recommended_iex_mw`
- `expected_tneb_mw`
- `expected_iex_price`
- `decision_reason`

## Current vs Proposed Separation

```text
Current system:
  Stores actual uploaded reports and calculates historical/dashboard metrics.

Proposed planning layer:
  Forecasts demand and IEX price, tracks solar expiry, and recommends tomorrow's procurement.
```

## Final Architecture View

```text
Client
│
├─ Solar Bank: client/month level
│  ├─ Solar allocation
│  ├─ Solar consumed
│  ├─ Solar remaining
│  └─ Expiry tracking
│
└─ Portfolio
   │
   ├─ Actual Data Layer
   │  ├─ Daily files
   │  ├─ Transactions
   │  └─ Energy schedule calculations
   │
   ├─ Forecast Layer
   │  ├─ Demand forecast
   │  └─ IEX price forecast
   │
   └─ Planning Layer
      ├─ Procurement plan
      ├─ 96 time-slot recommendation
      ├─ Expected cost
      ├─ Expected savings
      └─ Risk warning
```

## Key Design Principle

```text
Actual data and planning data should remain separate.

Actual data answers:
  What happened?

Planning data answers:
  What should we do tomorrow?
```
