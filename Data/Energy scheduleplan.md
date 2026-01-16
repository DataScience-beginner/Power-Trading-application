Yes, I Understand!
Let me confirm the workflow:

Current State:
✅ Parsers working (DOR & SCH)
✅ Database storing transactions
✅ Dashboard showing raw transaction data
Next Phase - Energy Schedule & Calculations:
Input: Excel template "IEX Purchase Data DEC 2022_Brookefields Mall.xlsx"

Auto-Fill Logic:

Row 4, 5, 6 (GDAM, DAM, RTM) ← from DOR files
Timestamped rows (00:00-00:15, 00:15-00:30...) ← from SCH Report "Consumption After Losses" section
Calculate: CTU Losses %, CTU Charges, Cost, NLDC App Fee
Monthly sheets: One sheet per month with day-wise data
Auto-update: When client uploads → Parse → DB → Transfer to Energy Schedule → Calculate → Dashboard
📋 User Stories Breakdown:
Epic 1: Energy Schedule Data Mapping
Story 1.1: Parse and extract "Consumption After Losses" from SCH files

Identify section in SCH PDF
Extract 96 time-slot data (15-min intervals)
Store in database with proper timestamp mapping
Story 1.2: Map DOR data (GDAM/DAM/RTM) to Energy Schedule format

Extract summary values from DOR files (CTU Losses %, CTU Charges, Cost)
Map to Row 4, 5, 6 structure
Handle multiple files per day (3 markets × 2 report types = 6 files)
Story 1.3: Create monthly Energy Schedule data model

Database schema for monthly aggregations
Day-wise data structure (1-31 days)
Link to source files (DOR/SCH)
Epic 2: Calculation Engine
Story 2.1: Implement CTU Losses calculation

Formula: % based on consumption
Apply to hourly slots
Story 2.2: Implement CTU Charges calculation

From DOR files
Per market type (GDAM/DAM/RTM)
Story 2.3: Implement NLDC App Fee calculation

Extract from DOR files
Daily aggregation
Story 2.4: Calculate Energy Savings

Formula: DOR vs SCH comparison
Deviation tracking
Cost impact
Epic 3: Auto-Transfer Workflow
Story 3.1: Create file upload to Energy Schedule pipeline

Trigger: When DOR/SCH uploaded
Auto-detect: Month, day, market type
Route to correct monthly sheet
Story 3.2: Build daily data aggregation service

Collect all 6 files for a day
Merge into single day view
Store in Energy Schedule format
Story 3.3: Monthly sheet generation

Auto-create sheet if month doesn't exist
Update existing day if re-upload
Version control for corrections
Epic 4: Dashboard Enhancement
Story 4.1: Energy Savings Summary Card

Total monthly savings
Daily average
Trend graph
Story 4.2: Detailed Day-wise View

Table: Date | DOR | SCH | Deviation | Savings
Drill-down to hourly view
Export to Excel
Story 4.3: Monthly Report Export

Generate Excel in template format
Pre-filled with all data
Download button
🎯 Execution Plan (Recommended Order):
Phase 1 - Foundation (Stories 1.1, 1.2, 1.3)
Build data extraction and mapping

Phase 2 - Calculations (Stories 2.1, 2.2, 2.3, 2.4)
Implement all calculation logic

Phase 3 - Automation (Stories 3.1, 3.2, 3.3)
Auto-transfer and sheet generation

Phase 4 - Visualization (Stories 4.1, 4.2, 4.3)
Dashboard updates and reporting

❓ Questions Before We Start:
Priority: Which story should we start with first?
SCH Format: Can you share a sample SCH file so I can see the "Consumption After Losses" section structure?
Calculations: Do you have the exact formulas for CTU Losses, Energy Savings?
Monthly Sheet: Should we create Excel files or store in database and show in dashboard?
Ready to start when you confirm! 🚀

