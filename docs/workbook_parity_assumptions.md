# Workbook Parity Assumptions

This note defines how the backend should treat the reference workbook during Excel-conversion testing. The workbook is the migration reference, but the backend corrected mode must be safe, explainable, and free from spreadsheet reference errors.

Reference workbook inspected locally:

```text
C:\Users\HP\Desktop\IEX Purchase Data_Client.xlsx
```

Do not send this workbook to the client. It is used only as an internal formula/reference source.

## Calculation modes

| Mode | Purpose | Behavior |
|---|---|---|
| `parity` | Match workbook behavior for known test cells | Preserves workbook-like formulas and spreadsheet error shapes where needed for QA. |
| `corrected` | Production-safe backend behavior | Avoids `#DIV/0!`, `#REF!`, stale references, and wrong-day references. Returns `null` for unsafe divisions. |
| `compare` | Internal QA | Returns parity and corrected values together with numeric differences. |

## Daily sheet outputs

These are the primary daily outputs used downstream.

| Workbook cell | Meaning | Backend field | Parity expectation |
|---|---|---|---|
| `B44` | Total IEX purchase price | `b44_iex_price` | Match workbook daily total for completed test days. |
| `B45` | IEX price per unit | `b45_iex_price_per_unit` | Match workbook when denominator exists; parity may show `#DIV/0!`. |
| `B46` | Equivalent EB price | `b46_eb_price` | Match workbook daily EB total for completed test days. |
| `B47` | Equivalent EB price per unit | `b47_eb_price_per_unit` | Match workbook when denominator exists; parity may show `#DIV/0!`. |

Known workbook sample values:

| Day | B44 | B45 | B46 | B47 |
|---:|---:|---:|---:|---:|
| 01 | 16224.506875251094 | 6.906321519136511 | 23125.188873804607 | 9.84375 |
| 02 | 16817.809393653144 | 6.638228531770892 | 28264.11973465008 | 11.15625 |
| 03 | 17359.692489439647 | 7.220414512898224 | 26822.43089913319 | 11.15625 |
| 04+ missing market data | 0 | `#DIV/0!` | 0 | `#DIV/0!` |

Corrected mode should return `null` for price-per-unit outputs when delivered units are zero.

## Energy Schedule input mapping

| Workbook area | Backend source |
|---|---|
| Market/date columns | `DailyFile.trading_date`, `DailyFile.report_type`, `DailyFile.sub_category` |
| GDAM values | `EnergyScheduleDay.gdam_*` fields derived from DOR-GDAM upload |
| DAM values | `EnergyScheduleDay.dam_*` fields derived from DOR-DAM upload |
| RTM values | `EnergyScheduleDay.rtm_*` fields derived from DOR-RTM upload |
| 96 slot quantities | `Transaction.quantity_mw` grouped into C1/C2/C4/C5 buckets |
| SCH after-loss schedule | `EnergyScheduleDay.consumption_after_losses_timeslots` and `total_consumption_after_losses_mwh` |
| Client consumption buckets | `EnergyScheduleConsumption.c1_kwh`, `c2_kwh`, `c4_kwh`, `c5_kwh` |

## Known workbook quirks to preserve only in parity mode

1. Day 01 STU system operating charge differs from later days.
   - Day `01` uses `=C3*$B$17`.
   - Day `02` and `03` use `=C3*$B$17/24`.
   - Backend parity mode keeps this day-01 behavior for matching.
   - Corrected mode uses the safer normalized divisor behavior.

2. Missing/zero market days produce spreadsheet errors.
   - Example: day `04` has `B45 = B44/B43` and `B47 = B46/B43` with zero denominator, so cached workbook output is `#DIV/0!`.
   - Backend corrected mode returns `null` instead of spreadsheet errors.

3. Savings Sheet has a wrong-day reference.
   - Row for day 08 uses `G11 = '07'!$B$47` while other same-row cells use day `08`.
   - Backend corrected mode uses the same day consistently.

4. Savings Sheet total row contains broken formulas.
   - `G35 = D35/#REF!`
   - `H35 = G35-F35`
   - Backend corrected mode computes safe averages/totals from numeric rows only.

5. Some workbook cached values may not match the visible formula precedent.
   - Example seen during inspection: a Savings Sheet line-loss formula can point to a blank Energy Schedule cell while the saved cached value still shows a number.
   - Backend corrected mode does not trust stale cached values; it derives line loss from the active calculation input.

## Savings Sheet backend rule

The backend builds Savings Sheet rows from daily outputs:

| Savings Sheet column | Backend source |
|---|---|
| IEX Price | daily `B44` |
| Equivalent EB Price | daily `B46` |
| Total Cost Saving | `B46 - B44` |
| IEX Price per Unit | daily `B45` |
| EB Price per Unit | daily `B47` |
| Cost Saving per Unit | `B47 - B45` |
| Bill for Exchange Purchase | daily `B44` |

Corrected mode totals use numeric-safe sums and averages. Error strings are not carried into final totals.

## Slot Wise Consolidate backend rule

The backend builds C1/C2/C4/C5 rows from daily bucket values:

| Slot Wise Consolidate column | Backend source |
|---|---|
| Consumption | `EnergyScheduleConsumption` bucket kWh |
| IEX Allotment | delivered IEX kWh grouped by bucket |
| Balance | consumption minus IEX delivered |

Workbook reference formulas:

| Slot | Consumption | IEX Allotment | Balance |
|---|---|---|---|
| C1 | `SUM('01:31'!J6)` | `SUM('01:31'!I6)` | `SUM('01:31'!K6)` |
| C2 | `SUM('01:31'!J7)` | `SUM('01:31'!I7)` | `SUM('01:31'!K7)` |
| C4 | `SUM('01:31'!J8)` | `SUM('01:31'!I8)` | `SUM('01:31'!K8)` |
| C5 | `SUM('01:31'!J9)` | `SUM('01:31'!I9)` | `SUM('01:31'!K9)` |

## QA rule before admin UI

For internal QA, use `GET /api/energy-schedule/calculation-trace` or `scripts/diagnostics/verify_excel_calculation_e2e.py` to confirm:

- required uploads are present;
- Energy Schedule DB values are populated;
- Consumption Details are present;
- daily B44/B45/B46/B47 outputs are produced;
- Savings Sheet and Slot Wise Consolidate summaries are produced;
- corrected outputs contain no spreadsheet error strings.
