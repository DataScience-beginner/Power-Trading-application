# Railway Database Fix - Quick Reference

## Problem Summary

**Issue**: Energy schedule shows "0 days completed" because SCH parser created 30 duplicate clients (IDs 8-37) instead of linking to the 5 correct clients (IDs 3-7).

**Root Cause**: SCH_Parser.py was extracting `entity_id` from filename (e.g., "IEX010126SCH") instead of reading it from Excel cells (e.g., "A2AR0NPT0001").

**Impact**:
- 450 DOR files → linked to clients 3-7 ✅
- 450 SCH files → created duplicate clients 8-37 ❌
- Energy schedule calculation requires DOR + SCH from **same client** → BROKEN

## Solution Overview

1. **Deploy fixes to Railway** (automated via GitHub push)
   - Database reset endpoint added to API
   - SCH parser fix already deployed

2. **Run systematic cleanup script**
   ```bash
   python fix_railway_database.py
   ```

3. **Verify results**
   - Check client count: Should be 5 clients
   - Check file count: Should be 900 files (450 DOR + 450 SCH)
   - Test energy schedule: Should show calculated days

## Deployment Status

### Just Deployed (waiting ~2 minutes for Railway):
- ✅ SCH parser fix (reads entity_id from Excel cells)
- ✅ Database reset endpoint (`POST /api/admin/reset-database`)
- ✅ Systematic fix script (`fix_railway_database.py`)

### How the Script Works:

```
Step 1: Health Check
  → Verify Railway API is responding

Step 2: Reset Database
  → DELETE all clients, portfolios, files, transactions
  → Requires typing "RESET" to confirm

Step 3: Upload DOR Files (450 files, ~12 minutes)
  → Creates 5 clean clients:
    1. Tata Power Company Limited
    2. Adani Power Limited
    3. Tamil Nadu Generation & Distribution Corp
    4. BSES Rajdhani Power Limited
    5. Bangalore Electricity Supply Company

Step 4: Verify Client Count
  → Should show 5 clients

Step 5: Upload SCH Files (450 files, ~12 minutes)
  → Links to existing clients (no duplicates!)
  → Uses fixed parser that reads entity_id from Excel

Step 6: Verify File Count
  → Should show 900 files total

Step 7: Test Energy Schedule Calculation
  → Calculates for Jan 2, 2026
  → Requires DOR from Jan 1 + SCH from Jan 2
  → Should show CTU losses and energy savings
```

## Manual Alternative (if script fails)

### Option 1: Use Railway PostgreSQL Console
```sql
-- Connect to Railway PostgreSQL
-- Delete all data
TRUNCATE TABLE transactions CASCADE;
TRUNCATE TABLE monthly_calculations CASCADE;
TRUNCATE TABLE energy_schedule_days CASCADE;
TRUNCATE TABLE energy_schedule_months CASCADE;
TRUNCATE TABLE daily_files CASCADE;
TRUNCATE TABLE portfolios CASCADE;
TRUNCATE TABLE clients CASCADE;
```

### Option 2: Use API Endpoint
```bash
# Reset database via API
curl -X POST https://power-trading-application-production.up.railway.app/api/admin/reset-database
```

Then manually upload files:
```bash
# Upload DOR files only
for file in Data/mock_reports/*DOR*.xls; do
    curl -X POST -F "file=@$file" \
         https://power-trading-application-production.up.railway.app/api/upload
done

# Wait for verification, then upload SCH files
for file in Data/mock_reports/*SCH*.xls; do
    curl -X POST -F "file=@$file" \
         https://power-trading-application-production.up.railway.app/api/upload
done
```

## Expected Results After Fix

### Dashboard Should Show:
- ✅ 5 clients (not 37)
- ✅ Energy schedule with >0 days completed
- ✅ Analytics displaying proper insights
- ✅ Client-specific filtering working
- ✅ Monthly/weekly reports functional

### Database Should Have:
- 5 clients (Tata, Adani, TNEB, BSES, BESCOM)
- ~10 portfolios (2 per client: NPT0001_TN0, NPT0001_KA0, etc.)
- 900 daily files (30 days × 6 file types × 5 clients)
- ~86,400 transactions (900 files × 96 timeslots)
- Energy schedule calculations for 29 days (Jan 2-30, 2026)

## Verification Checklist

After running the fix script:

- [ ] Railway deployment completed (~2 min wait)
- [ ] fix_railway_database.py ran successfully
- [ ] Database shows 5 clients
- [ ] Database shows 900 files
- [ ] Energy schedule calculation works for Jan 2
- [ ] Dashboard shows calculated days (>0)
- [ ] Analytics display insights (not 0.00)
- [ ] Client filtering works
- [ ] No duplicate clients (IEX*SCH pattern)

## Troubleshooting

### If clients still show duplicates:
→ SCH parser fix not deployed yet. Wait for Railway, then re-run script.

### If energy schedule still shows 0 days:
→ Check calculation endpoint response for errors
→ Verify DOR and SCH files are under same client_id

### If analytics show 0.00:
→ Separate issue: PostgreSQL SQL compatibility (next todo item)
→ Analytics uses SQLite functions, needs PostgreSQL rewrite

### If upload fails:
→ Check Railway logs for parser errors
→ Verify file format matches expected structure
→ Test single file upload via dashboard UI

## Timeline

**Total Fix Time**: ~30 minutes
- Railway deployment: 2 minutes
- Database reset: 10 seconds
- DOR upload: 12 minutes
- SCH upload: 12 minutes
- Verification: 5 minutes

## Next Steps After Database Fix

1. **Fix Analytics SQL** (PostgreSQL compatibility)
   - Replace `strftime()` with PostgreSQL date functions
   - Update analytics endpoint queries

2. **Fix Client-Specific Filtering**
   - Dashboard should filter energy schedule by selected client
   - Likely a frontend state management issue

3. **Test Complete Workflow**
   - Demo to cofounder with working energy schedule
   - Show CTU loss calculations
   - Show energy savings insights

## Support

If issues persist:
1. Check Railway logs: `railway logs`
2. Check database status: `GET /api/clients`
3. Test single upload: `POST /api/upload` with one file
4. Review parser output in Railway logs
