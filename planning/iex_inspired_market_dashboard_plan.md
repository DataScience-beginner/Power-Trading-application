# IEX-Inspired Market Dashboard Product Layer

## Purpose

The authenticated workspace should make upload, schedule calculation, and market review obvious to enterprise users. The IEX market snapshot pattern is useful because power trading users already understand terms such as market snapshot, aggregate demand/supply, interval, delivery period, MCP, MCV, and scheduled volume.

## Implemented product concepts

- Clear top action buttons instead of icon-only actions.
- Dedicated Upload Center for DAM/RTM/GDAM, SCH/DOR, workbook, solar allocation, and client master-data flows.
- Market Snapshot page with:
  - interval and delivery-period controls;
  - market snapshot tabs;
  - KPI cards;
  - MCP price trend;
  - purchase bid versus sell bid chart;
  - Solar / IEX / TNEB source mix with scheduled volume;
  - 15-minute block table.

## Chart library decision

The public IEX page did not expose a reliable chart-library identifier from static inspection. The current app already uses Recharts, so this implementation keeps Recharts to avoid adding another dependency and to stay consistent with the existing frontend.

## Next backend/data milestone

The current Market Snapshot page uses product-shape sample rows. The next milestone should create a backend endpoint that returns real market/schedule rows from uploaded data:

```text
GET /api/market-snapshot
```

Recommended response shape:

```text
date
hour
time_block
portfolio_code
purchase_bid_mw
sell_bid_mw
mcv_mw
scheduled_mw
solar_mw
iex_mw
tneb_mw
mcp_rs_per_mwh
```

