# 🚀 Quick Dashboard Tutorial (5 Minutes)

## Step 1: Open Dashboard (30 seconds)

1. Open browser
2. Go to: `http://localhost:8000/frontend/dashboard.html`
3. You'll see the main dashboard with stats and charts

**What you see:**
```
┌─────────────┬──────────────────────────────────────┐
│  Sidebar    │         Main Dashboard               │
│             │  [Stats Cards]                       │
│ ⚡PowerTrade│  ┌─────┬─────┬─────┬─────┐          │
│             │  │ DOR │ SCH │Total│ Net │          │
│ 📊Dashboard │  └─────┴─────┴─────┴─────┘          │
│ 📈Analytics │  [DOR vs SCH Chart]                  │
│ ⚖️DOR vs SCH│  [Other Charts]                      │
│             │  [Transaction Table]                 │
│ 📋Trans...  │                                      │
│ 📤Upload    │                                      │
│             │  Admin Mode: [OFF] 👈 Top Right     │
└─────────────┴──────────────────────────────────────┘
```

---

## Step 2: View Your Data (1 minute)

### Check Summary Stats
Look at the 4 cards at top:
- **DOR Files**: 2 (planned trades)
- **SCH Files**: 0 (actual schedules)
- **Total Transactions**: 192
- **Net Amount**: ₹-4,930.82

### Understand DOR vs SCH Chart
- **Purple line** = What you PLANNED (DOR)
- **Pink line** = What ACTUALLY happened (SCH)
- Currently only DOR data since no SCH files uploaded yet

---

## Step 3: Filter Data (1 minute)

### Select Portfolio
```
Top Bar → Portfolio dropdown → Select "S2TN0NPT0019"
```

### Choose Time Period
```
Top Bar → View Type → Monthly (already selected)
Top Bar → Month → Select "January 2026"
Click "Apply Filters" button
```

### Set Custom Date Range
```
Start Date: 2026-01-01
End Date: 2026-01-31
Click "Apply Filters"
```

---

## Step 4: Upload New File (1.5 minutes)

### Navigate to Upload
1. Click "📤 Upload Files" in sidebar
2. You'll see upload area

### Upload a File
1. **Report Type**: Select "DOR" or "SCH"
2. **Sub Type**: Select "GDAM", "RTM", or "DAM"
3. Drag & drop file OR click to browse
4. Watch upload progress
5. Success message appears
6. Data automatically reloads

**Example:**
```
Upload: IEX130126SCH_NPT0019_TN0_Grasim.xlsx
Type: SCH (Lag Indicator)
Sub: DAM
Result: ✅ Success - Now you can compare DOR vs SCH!
```

---

## Step 5: Admin Features (1 minute)

⚠️ **Admin Only - For Corrections**

### Enable Admin Mode
1. Look at top-right corner
2. Find "Admin Mode" toggle (currently OFF/gray)
3. Click toggle → turns ORANGE
4. Alert: "⚠️ Admin Mode Enabled"

### Edit a Transaction
1. Scroll to transaction table
2. "Edit" buttons now visible in last column
3. Click "Edit" on any row
4. Modal opens with fields:
   - Time Slot (read-only)
   - Quantity (MW) - editable
   - Rate (₹/MWh) - editable
   - Amount (₹) - editable
5. Change values
6. Click "Save Changes"
7. Database updates instantly!

**Example Edit:**
```
Before:
  Quantity: 0.20 MW
  Rate: 2,500.86 ₹/MWh
  
After Admin Edit:
  Quantity: 0.25 MW ✏️
  Rate: 2,600.00 ₹/MWh ✏️
  
Saved! ✅
```

---

## 🎯 Key Features Recap

| Feature | How to Access | Use Case |
|---------|---------------|----------|
| **Dashboard** | Sidebar → Dashboard | Overview of all data |
| **Portfolio Switch** | Top bar dropdown | See specific portfolio |
| **Date Range** | Top bar date pickers | Historical analysis |
| **DOR vs SCH** | Main chart | Compare planned vs actual |
| **Upload** | Sidebar → Upload | Add new data files |
| **Admin Edit** | Toggle ON → Edit button | Fix incorrect values |

---

## 🔍 Common Tasks

### Task 1: "Show me last month's performance"
```
1. View Type → Monthly
2. Month → Select previous month
3. Apply Filters
4. Check DOR vs SCH chart for variance
```

### Task 2: "Compare two portfolios"
```
1. Open dashboard in two browser tabs
2. Tab 1: Portfolio A
3. Tab 2: Portfolio B
4. View side-by-side
```

### Task 3: "Fix wrong data entry"
```
1. Enable Admin Mode (top-right toggle)
2. Find transaction in table
3. Click "Edit"
4. Correct values
5. Save
```

### Task 4: "Export this month's data"
```
1. Set filters for current month
2. Click "📥 Export CSV" button above table
3. Download opens
4. Use in Excel/analysis
```

---

## 📊 Reading the Charts

### 1. DOR vs SCH Comparison (Line Chart)
```
Perfect Execution:     Variance:
   MW                     MW
    │                      │  
0.3 │     ■■■■■■          0.3│    ■■■  (DOR higher)
0.2 │    ■ ■ ■ ■          0.2│   ■   ■■
0.1 │   ■   ■   ■         0.1│  ■      ■ (SCH lower)
    └─────────────          └──────────
    00:00  12:00  24:00       00:00 12:00 24:00
    
    Purple = DOR            Gap = Execution issue
    Pink = SCH
```

### 2. Buy vs Sell (Doughnut)
```
     100%
    ┌────┐
    │ 🔴 │ ← Red = Buy (100%)
    │ 🟢 │ ← Green = Sell (0%)
    └────┘
    
Balanced:              Imbalanced:
   50%                    80%
  ┌──┐                  ┌────┐
  │🔴│                  │ 🔴 │
  │🟢│                  │🟢  │
  └──┘                  └────┘
```

### 3. Peak Hours (Bar Chart)
```
MW
 │        ■■■
 │      ■■■■■■
 │    ■■■■■■■■
 │  ■■■■■■■■■■
 └────────────────
   00-04  12-16  20-24
   Low   High    Med
```

---

## 💡 Pro Tips

1. **Bookmark Filters**: After setting filters, bookmark the page
2. **Keyboard Shortcuts**: 
   - Ctrl+F: Search in table
   - Tab: Navigate filters quickly
3. **Multi-View**: Open multiple tabs for comparison
4. **Export Regular**: Download data weekly for backup
5. **Admin Care**: Only enable when editing, disable after

---

## ❗ Important Notes

### DOR vs SCH Meaning
- **DOR (Lead)**: What you PLAN to trade tomorrow
- **SCH (Lag)**: What you ACTUALLY traded today
- **Gap**: Your execution accuracy

### Why It Matters
```
Example:
DOR says: "We'll buy 1.5 MW during peak hours"
SCH says: "We bought 1.3 MW during peak hours"
Gap: -0.2 MW (13% under-execution)

Action: Investigate why 13% didn't execute
```

### File Limit
- **Maximum 6 files per portfolio per day**
  - 3 DOR (GDAM, RTM, DAM)
  - 3 SCH (GDAM, RTM, DAM)
- Re-uploading same type replaces old one

---

## 🆘 Need Help?

### Dashboard not loading?
```bash
# Check server is running:
curl http://localhost:8000/api/health

# Should return:
{"status":"healthy",...}
```

### No data showing?
1. Verify files uploaded
2. Check date range includes data
3. Clear browser cache

### Charts blank?
1. F12 → Console → Check errors
2. Verify internet (Chart.js CDN)
3. Refresh page

---

## ✅ Quick Checklist

After 5 minutes, you should be able to:
- [ ] Open dashboard
- [ ] View summary stats
- [ ] Change portfolio filter
- [ ] Select date range
- [ ] Upload a file
- [ ] Enable admin mode
- [ ] Edit a transaction
- [ ] Export data

**Congratulations! You're ready to use the dashboard! 🎉**

---

## 📚 Learn More

- Full Guide: See `DASHBOARD_GUIDE.md`
- Database: See `DATABASE_GUIDE.md`
- Parsers: See `PARSERS_GUIDE.md`
- API Docs: Visit `http://localhost:8000/docs`

---

**Next:** Start uploading your SCH files to see DOR vs SCH comparison!
