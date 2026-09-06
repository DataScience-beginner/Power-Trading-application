# Remaining Excel Automation Todo List

This list continues from the backend Excel-conversion work already completed.

## Current checkpoint

Backend calculation foundation is in place:

- Upload flow stores DOR/SCH files in database.
- Energy schedule DB rows are built from uploaded files.
- Consumption Details storage exists for manual and upload inputs.
- Daily calculations produce B44, B45, B46, and B47.
- Savings Sheet and Slot Wise Consolidate equivalents exist in backend.
- E2E diagnostic verifies upload -> DB -> consumption -> calculation.

## Phase 1 - Backend readiness tightening

1. [Done] Make the E2E diagnostic output compact.
   - Reduce parser/upload log noise.
   - Keep only pass/fail, file counts, transaction counts, missing inputs, and key calculation outputs.

2. [Done] Add an internal QA trace endpoint or script.
   - Show uploaded files used.
   - Show DB fields used for Energy Schedule.
   - Show consumption inputs used.
   - Show daily B44/B45/B46/B47 outputs.
   - Show Savings Sheet and Slot Wise Consolidate summaries.

3. [Done] Add controlled test consumption dataset.
   - Seed day 01, 02, 03 consumption for testing.
   - Mark source as diagnostic/test seed.
   - Avoid treating this as production/client data.

4. [Done] Validate multiple-day calculation.
   - Run day 01 only.
   - Run days 01-03.
   - Run full month with incomplete days.
   - Confirm corrected mode does not break on missing/zero data.

5. [Done] Confirm workbook parity assumptions.
   - List known workbook quirks separately.
   - Confirm which outputs should match Excel exactly.
   - Confirm which outputs should use corrected backend behavior.

## Phase 2 - Admin/internal UI

1. [Done] Add admin calculation review screen.
   - Portfolio selector.
   - Year/month/day selector.
   - Calculate button.
   - Comparison view: parity vs corrected.
   - Missing input status.

2. [Done] Add Consumption Details UI.
   - Manual daily entry for C1/C2/C4/C5/base tariff.
   - Monthly upload option.
   - Existing consumption table.

3. [Done] Add Energy Schedule trace view.
   - Show market upload coverage: GDAM, DAM, RTM, SCH.
   - Show derived Energy Schedule values.
   - Show slot-wise bucket summary.

4. [Done] Add internal QA indicators.
   - Complete/incomplete days.
   - Missing files.
   - Missing consumption.
   - Calculation version.
   - Last calculated timestamp.

## Phase 3 - Persistence and audit

1. [Done] Persist month-level calculation summary.
   - Daily rows.
   - Savings Sheet totals.
   - Slot Wise Consolidate totals.

2. [Done] Store calculation audit fields.
   - Raw source file IDs.
   - Consumption source.
   - Calculation mode.
   - Calculation version.
   - Assumptions used.

3. [Done] Add retrieval endpoint for saved calculation results.
   - Read latest calculation for portfolio/month.
   - Avoid recalculating unless user requests rerun.

## Phase 4 - Client-facing report, later

1. [Done] Design final Excel output.
   - Clean layout only.
   - Hide internal QA/parity fields.
   - Include controlled assumptions.

2. [Done] Generate Excel report from trusted backend results.

3. [Done] Generate PDF summary from trusted backend results.

4. [Done] Add export endpoints only after internal UI is trusted.

## Suggested next task

Excel and PDF exports are available from saved monthly summaries. Next: perform manual UI smoke test with uploaded/seeded data and review downloaded files.



