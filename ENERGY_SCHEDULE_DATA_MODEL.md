# Energy Schedule Data Model - Documentation

## Overview
The Energy Schedule data model stores monthly day-wise DOR + SCH data with automatic calculations for energy savings tracking.

## Story 1.3 Completion ✅
This data model fulfills Story 1.3: "Create Energy Schedule data model for monthly day-wise storage"

## Database Schema

### Table 1: `energy_schedule_months`
Monthly container for Energy Schedule sheets (one per portfolio per month).

**Columns:**
- `id` - Primary key
- `portfolio_id` - Foreign key to portfolios table
- `year` - Year (e.g., 2026)
- `month` - Month (1-12)
- `month_name` - Display name (e.g., "January 2026")
- **Summary Metrics** (aggregated from daily entries):
  - `total_scheduled_mwh` - Total scheduled quantity
  - `total_consumption_after_losses_mwh` - Total consumption
  - `total_energy_savings_mwh` - Total energy savings
  - `total_gdam_cost`, `total_dam_cost`, `total_rtm_cost` - Market-wise costs
  - `average_ctu_losses_percent` - Average CTU losses
- `days_completed` - Number of days with complete data
- `is_complete` - Flag (1 if all days filled, 0 otherwise)
- `created_at`, `updated_at` - Timestamps

**Relationships:**
- Belongs to: `Portfolio`
- Has many: `EnergyScheduleDay` (up to 31 days)

---

### Table 2: `energy_schedule_days`
Daily Energy Schedule entries with DOR + SCH data and calculations.

**Columns:**

#### Metadata
- `id` - Primary key
- `month_sheet_id` - Foreign key to energy_schedule_months
- `trading_date` - Trading date
- `day_of_month` - Day (1-31)

#### DOR Summary Data (Row 4: GDAM)
- `gdam_nldc_fee` - NLDC Application Fee
- `gdam_ctu_charges` - CTU Transmission Charges
- `gdam_cost` - Total cost
- `gdam_scheduled_quantity_mwh` - Scheduled quantity
- `gdam_other_charges` - JSON: STU, SLDC, Fees

#### DOR Summary Data (Row 5: DAM)
- `dam_nldc_fee`, `dam_ctu_charges`, `dam_cost`
- `dam_scheduled_quantity_mwh`, `dam_other_charges`

#### DOR Summary Data (Row 6: RTM)
- `rtm_nldc_fee`, `rtm_ctu_charges`, `rtm_cost`
- `rtm_scheduled_quantity_mwh`, `rtm_other_charges`

#### SCH Consumption Data (Timestamped Rows)
- `consumption_after_losses_timeslots` - JSON array of 96 values
- `total_consumption_after_losses_mwh` - Total consumption
- `regional_loss_percent` - Regional loss (e.g., 4.81%)
- `state_loss_percent` - State loss (e.g., 3.06%)
- `combined_loss_percent` - Combined loss (e.g., 7.87%)

#### Calculated Fields
- `total_scheduled_mwh` - Sum of GDAM + DAM + RTM scheduled
- `ctu_losses_percent` - (Scheduled - Consumption) / Scheduled × 100
- `ctu_losses_mwh` - Absolute CTU losses
- `energy_savings_mwh` - Energy savings (equals CTU losses)
- `total_nldc_fee` - Sum of all NLDC fees
- `total_ctu_charges` - Sum of all CTU charges
- `total_cost` - Total cost across all markets

#### Data Completeness Flags
- `has_gdam_data` - 1 if GDAM file uploaded
- `has_dam_data` - 1 if DAM file uploaded
- `has_rtm_data` - 1 if RTM file uploaded
- `has_sch_data` - 1 if SCH file uploaded
- `is_complete` - 1 if all 4 files present and calculated

#### Timestamps
- `created_at`, `updated_at`, `calculated_at`

**Relationships:**
- Belongs to: `EnergyScheduleMonth`

---

## Data Model Hierarchy

```
Portfolio
  └─> EnergyScheduleMonth (one per month)
        └─> EnergyScheduleDay (1-31 days)
              ├─> DOR Summary Data (GDAM, DAM, RTM)
              ├─> SCH Consumption Data (96 timeslots)
              └─> Calculated Fields (auto-computed)
```

---

## CRUD Operations

### File: `database/energy_schedule_crud.py`

#### Month Sheet Operations

**`get_or_create_month_sheet(db, portfolio_id, year, month)`**
- Gets existing month sheet or creates new one
- Returns: `EnergyScheduleMonth` object

**`get_month_sheet(db, portfolio_id, year, month)`**
- Gets month sheet if exists
- Returns: `EnergyScheduleMonth` or `None`

**`get_all_month_sheets(db, portfolio_id=None)`**
- Lists all month sheets, optionally filtered by portfolio
- Returns: List of `EnergyScheduleMonth`

**`update_month_summary(db, month_sheet_id)`**
- Recalculates month aggregates from daily entries
- Auto-called when daily entries are updated
- Returns: Updated `EnergyScheduleMonth`

**`delete_month_sheet(db, month_sheet_id)`**
- Deletes month sheet and all daily entries (cascade)
- Returns: `True`/`False`

---

#### Daily Entry Operations

**`get_or_create_daily_entry(db, portfolio_id, trading_date)`**
- Gets or creates daily entry
- Auto-creates month sheet if needed
- Returns: `EnergyScheduleDay` object

**`update_daily_entry_dor_data(db, daily_entry_id, market_type, dor_data)`**
- Updates DOR summary data for GDAM/DAM/RTM
- `market_type`: "GDAM", "DAM", or "RTM"
- `dor_data`: Output from `DOR_EnergySchedule_Parser`
- Returns: Updated `EnergyScheduleDay`

**`update_daily_entry_sch_data(db, daily_entry_id, sch_data)`**
- Updates SCH consumption data
- `sch_data`: Output from `SCH_Energy_Schedule_Parser`
- Returns: Updated `EnergyScheduleDay`

**`calculate_daily_entry(db, daily_entry_id)`**
- Calculates all derived fields:
  - Total scheduled MWh
  - CTU losses % and MWh
  - Energy savings
  - Total charges
- Auto-updates month summary
- Returns: Updated `EnergyScheduleDay`

**`get_daily_entry_by_date(db, portfolio_id, trading_date)`**
- Gets daily entry for specific date
- Returns: `EnergyScheduleDay` or `None`

**`get_all_daily_entries(db, month_sheet_id)`**
- Lists all daily entries in a month
- Returns: List of `EnergyScheduleDay` (ordered by date)

**`delete_daily_entry(db, daily_entry_id)`**
- Deletes daily entry, updates month summary
- Returns: `True`/`False`

---

## Usage Example

```python
from database.config import SessionLocal
from database.energy_schedule_crud import (
    get_or_create_daily_entry,
    update_daily_entry_dor_data,
    update_daily_entry_sch_data,
    calculate_daily_entry
)
from parsers.DOR_EnergySchedule_Parser import DOR_EnergyScheduleParser
from parsers.SCH_Energy_Schedule_Parser import SCH_EnergyScheduleParser
from datetime import date

db = SessionLocal()

# Parse DOR file
dor_parser = DOR_EnergyScheduleParser("Data/GDAM_DOR_file.xls")
gdam_data = dor_parser.parse()

# Parse SCH file
sch_parser = SCH_EnergyScheduleParser("Data/SCH_file.xlsx")
sch_data = sch_parser.parse()

# Get or create daily entry
trading_date = date(2026, 1, 12)
daily_entry = get_or_create_daily_entry(db, portfolio_id=1, trading_date=trading_date)

# Update with DOR data
daily_entry = update_daily_entry_dor_data(
    db, daily_entry.id, "GDAM", gdam_data
)

# Update with SCH data
daily_entry = update_daily_entry_sch_data(
    db, daily_entry.id, sch_data
)

# Calculate derived fields
daily_entry = calculate_daily_entry(db, daily_entry.id)

print(f"Energy Savings: {daily_entry.energy_savings_mwh} MWh")
print(f"CTU Losses: {daily_entry.ctu_losses_percent:.2f}%")

db.close()
```

---

## Test Results

**Test File:** `test_energy_schedule_model.py`

**Output:**
```
Portfolio: NPT0027_KA0
Month Sheet: January 2026

CALCULATION RESULTS:
─────────────────────────────────────────
Total Scheduled:           53.50 MWh
Consumption After Losses:  48.50 MWh
CTU Losses:                5.00 MWh (9.35%)
Energy Savings:            5.00 MWh
Total NLDC Fee:            ₹-15.78
Total CTU Charges:         ₹-1391.72
Total Cost:                ₹1662479.66
Data Complete:             ✅ YES

MONTH SUMMARY (January 2026):
─────────────────────────────────────────
Total Scheduled:           53.50 MWh
Total Consumption:         48.50 MWh
Total Energy Savings:      5.00 MWh
Total GDAM Cost:           ₹1674432.76
Total DAM Cost:            ₹-6396.66
Total RTM Cost:            ₹-5556.44
Average CTU Losses:        9.35%
Days Completed:            1/31
```

---

## Data Flow

```
1. Upload DOR files (GDAM/DAM/RTM) → Parse with DOR_EnergySchedule_Parser
2. Upload SCH file → Parse with SCH_Energy_Schedule_Parser
3. Create/update daily entry:
   a. update_daily_entry_dor_data() for each market
   b. update_daily_entry_sch_data() for consumption
4. Calculate derived fields:
   c. calculate_daily_entry() → Auto-computes CTU losses, energy savings
5. Month summary auto-updates when daily entries change
```

---

## Automatic Calculations

### Formula: CTU Losses %
```
CTU Losses % = (Total Scheduled - Consumption After Losses) / Total Scheduled × 100
```

**Where:**
- Total Scheduled = GDAM Scheduled + DAM Scheduled + RTM Scheduled
- Consumption After Losses = From SCH file

### Formula: Energy Savings (MWh)
```
Energy Savings = CTU Losses (MWh)
Energy Savings = Total Scheduled - Consumption After Losses
```

### Month Aggregation
Month summaries are auto-calculated from daily entries:
- Sum of all daily scheduled quantities
- Sum of all daily consumption
- Sum of all daily energy savings
- Weighted average CTU losses %

---

## Integration with Existing Tables

The Energy Schedule model integrates seamlessly with existing database:

```
Client (entity_id, entity_name)
  └─> Portfolio (portfolio_code)
        ├─> DailyFile (DOR/SCH files, transactions)
        └─> EnergyScheduleMonth (monthly sheets)
              └─> EnergyScheduleDay (daily summaries + calculations)
```

**Key difference:**
- `DailyFile` + `Transaction`: Stores raw transactional data (96 timeslots)
- `EnergyScheduleDay`: Stores summary data + calculations

---

## Next Steps

**Story 2.1-2.4**: Implement remaining calculations
- Story 2.1: CTU Losses % formula refinement
- Story 2.2: CTU Charges calculation
- Story 2.3: NLDC Fee aggregation
- Story 2.4: Energy Savings summary dashboard

**Story 3.1-3.3**: Auto-transfer workflow
- Auto-create daily entries when files uploaded
- Auto-trigger calculations when all 4 files present
- Background job for monthly summary updates

**Story 4.1-4.3**: Dashboard enhancements
- Energy Schedule view in React dashboard
- Monthly summary charts
- Day-wise drill-down tables

---

## Files Created

1. **Database Models**: `database/models.py` (added `EnergyScheduleMonth` and `EnergyScheduleDay`)
2. **CRUD Operations**: `database/energy_schedule_crud.py` (15+ functions)
3. **Migration**: Auto-created tables via SQLAlchemy `Base.metadata.create_all()`
4. **Test Script**: `test_energy_schedule_model.py` (complete workflow test)

---

## Database Tables

Run this to verify tables created:
```bash
sqlite3 power_trading.db ".tables"
```

Expected output:
```
clients
daily_files
energy_schedule_days     # ← NEW
energy_schedule_months   # ← NEW
monthly_calculations
portfolios
transactions
```

---

## Author
Power Trading Application Team  
Date: January 16, 2026
