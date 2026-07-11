# Complete Railway Deployment Guide

## Current Issues on Railway:
- ❌ Old backend code (transactions limited to 1000)
- ❌ Old/incorrect data (1124 files instead of 42)
- ❌ No energy schedule data
- ❌ Analytics summary returning empty fields
- ❌ Browser errors (service worker, manifest.json 404s)

## Solution: Fresh Deployment

### Step 1: Commit and Push Latest Code

Run this in PowerShell:
```powershell
cd 'c:\Users\balr\OneDrive - TOPSOE\GitHub\Personal test projets\Power-trading\Power-Trading-application'

# Add all changes
git add .

# Commit with message
git commit -m "Fix: Dashboard analytics, energy schedule, and API improvements"

# Push to GitHub (will trigger Railway auto-deploy)
git push origin main
```

### Step 2: Wait for Railway Deployment

1. Go to https://railway.app/dashboard
2. Open your Power-Trading-application project
3. Watch the deployment logs
4. Wait for "Build successful" and "Deployment live" messages
5. This should take 2-5 minutes

### Step 3: Clean Railway Database

After deployment completes, run:
```powershell
python clean_railway_database.py
```

### Step 4: Upload Fresh Data to Railway

```powershell
# Upload the 7-day mock data (Jan 10-16, 2026)
python upload_to_railway_fresh.py

# Populate energy schedule data
python populate_railway_energy_schedule.py
```

### Step 5: Verify Deployment

1. Open your Railway URL: https://power-trading-application-production.up.railway.app
2. Hard refresh browser: **Ctrl + Shift + R** (or Cmd + Shift + R on Mac)
3. Check dashboard shows:
   - DOR Files: 21
   - SCH Files: 21
   - Total Transactions: 6,048
   - Energy Schedule section populated

### Step 6: Test API Endpoints

Run to verify:
```powershell
python test_railway_api.py
```

Expected results:
- Analytics summary: Shows dor_count, sch_count, total_transactions
- Transactions: 6,048 total
- Energy schedule: 6 days, 1 month record

---

## If Auto-Deploy Doesn't Work

Manually trigger deployment in Railway:
1. Go to Railway dashboard → Your project
2. Click on the service
3. Click "Deploy" → "Redeploy"

---

## Quick One-Command Solution

Or just run:
```powershell
.\complete_railway_deploy.bat
```

This will do all steps automatically!
