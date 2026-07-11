# 📦 Power Trading Dashboard - Portable Package

## 🎯 Quick Start - For Co-Founder

Hey! This is a complete, ready-to-run Power Trading Analytics Dashboard. Everything you need is in this folder.

### ⚡ One-Command Setup

**macOS/Linux:**
```bash
./bootstrap.sh
```

**Windows:**
- Double-click `bootstrap.bat`
- OR open CMD/PowerShell and run: `.\bootstrap.bat`

**That's it!** The dashboard will open at `http://localhost:3000`

---

## 📋 Prerequisites (Install These First)

Before running bootstrap, install:

1. **Python 3.8 or higher**
   - Download: https://www.python.org/downloads/
   - ✅ During installation, check "Add Python to PATH"

2. **Node.js 16 or higher** (LTS version recommended)
   - Download: https://nodejs.org/

### How to Check if Already Installed

Open terminal/CMD and run:
```bash
python --version    # Should show 3.8 or higher
node --version      # Should show 16 or higher
```

If both show versions, you're ready to go!

---

## 🚀 Running the Application

### First Time Setup (~2-3 minutes)

1. **Extract this ZIP file** to any folder
2. **Open terminal/CMD** in that folder
3. **Run bootstrap script:**
   - macOS/Linux: `chmod +x bootstrap.sh && ./bootstrap.sh`
   - Windows: Double-click `bootstrap.bat`

The script will:
- ✅ Install all required packages (Python + Node.js)
- ✅ Create database with sample data (2,072 transactions)
- ✅ Start backend server (port 8000)
- ✅ Start frontend dashboard (port 3000)
- ✅ Open in your browser automatically

### Subsequent Runs (~10 seconds)

Just run bootstrap again - it skips already-installed packages.

---

## 🌐 Accessing the Dashboard

Once setup completes, open your browser:

```
http://localhost:3000
```

### What You'll See:

**4 Main Tabs:**

1. **Dashboard**
   - Overview statistics (files, transactions, amounts)
   - Client selection from sidebar
   - Transaction table with filters
   - Hourly distribution charts

2. **Energy Schedule**
   - Switch between Hourly/Daily/Weekly/Monthly views
   - Interactive line charts showing energy data
   - Detailed data tables with calculations
   - CTU losses and energy savings analysis

3. **Analytics**
   - Market volume analysis
   - Daily volume trends
   - Hourly patterns (line charts)
   - Report distribution (pie chart)
   - Price analysis by market type (GDAM/DAM/RTM)

4. **Reports**
   - Download Daily Trading Report (PDF/Excel)
   - Download Energy Schedule Report (PDF)
   - View recently generated reports

---

## 📊 Sample Data

The application includes realistic test data:

- **Client**: Mellbro Sugars Pvt Ltd (Portfolio: NPT0027_KA0)
- **Date Range**: January 1-15, 2026
- **Total Transactions**: 2,072 records
- **Markets**: GDAM (Day-Ahead), DAM (Day-Ahead Market), RTM (Real-Time)
- **Report Types**: DOR (Daily Obligation Reports), SCH (Scheduling Reports)

This lets you test all features without uploading actual files.

---

## 🧪 What to Test

### Basic Navigation
- ✅ Select "Mellbro Sugars Pvt Ltd" from sidebar
- ✅ Switch between Dashboard/Energy Schedule/Analytics/Reports tabs
- ✅ Try different date ranges (if available)

### Dashboard Features
- ✅ View summary statistics at the top
- ✅ Filter by report type (DOR/SCH)
- ✅ Filter by market type (GDAM/DAM/RTM)
- ✅ Scroll through transaction table
- ✅ Check hourly distribution chart

### Energy Schedule
- ✅ Switch view mode: Hourly → Daily → Weekly → Monthly
- ✅ Observe how charts update
- ✅ Check data tables below charts
- ✅ Verify calculations make sense

### Analytics
- ✅ Review market volume chart
- ✅ Check daily volume trends
- ✅ Examine hourly patterns (should be line chart)
- ✅ Look at report distribution pie chart
- ✅ Compare prices across GDAM/DAM/RTM

### Reports (Most Important!)
- ✅ Click "Export PDF" on Daily Trading Report card
- ✅ Verify PDF downloads and opens correctly
- ✅ Click "Export Excel" on Daily Trading Report card
- ✅ Verify Excel downloads and opens correctly
- ✅ Check if data in reports matches dashboard
- ✅ Try Energy Schedule PDF export

---

## 🐛 Troubleshooting

### "Port 8000 already in use"
**Solution**: Another program is using port 8000
```bash
# Find and kill the process
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

### "Port 3000 already in use"
Same solution as above, but for port 3000.

### "Python not found"
- Make sure Python is installed
- Windows: Check "Add to PATH" during installation
- Restart terminal after installing

### "Node not found"
- Install Node.js from https://nodejs.org
- Restart terminal after installing

### Database errors
Delete `power_trading.db` file and run bootstrap again.

### Dependency installation fails
**For Python:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**For Node.js:**
```bash
cd frontend-react
rm -rf node_modules package-lock.json
npm install
```

### Can't access http://localhost:3000
- Check if frontend started successfully (look for errors)
- Check `frontend.log` file
- Try a different browser
- Clear browser cache

---

## 🛑 Stopping the Application

### macOS/Linux:
```bash
./shutdown.sh
```

### Windows:
- Press `Ctrl+C` in the terminal where bootstrap is running
- OR close the terminal window
- OR kill processes manually:
  ```cmd
  taskkill /F /IM python.exe
  taskkill /F /IM node.exe
  ```

---

## 📁 Project Structure

```
Power-Trading-application/
├── bootstrap.sh              # Setup script (macOS/Linux)
├── bootstrap.bat             # Setup script (Windows)
├── shutdown.sh               # Stop script
├── SETUP_INSTRUCTIONS.md     # This file
├── requirements.txt          # Python packages
├── package.json              # Node.js config
├── power_trading.db          # SQLite database (created on first run)
│
├── api/
│   ├── main.py              # FastAPI backend (18+ endpoints)
│   └── report_generator.py  # PDF/Excel generation
│
├── database/
│   ├── models.py            # Database schema
│   ├── services.py          # Business logic
│   └── energy_schedule_service.py  # Calculations
│
├── frontend-react/
│   ├── src/
│   │   ├── pages/           # Dashboard, Analytics, Reports
│   │   ├── components/      # Reusable UI components
│   │   └── services/        # API calls
│   └── package.json
│
├── parsers/
│   ├── DOR_Parser.py        # Parse DOR Excel files
│   └── SCH_Parser.py        # Parse SCH Excel files
│
└── Data/
    └── mock_reports/        # Sample Excel files (if included)
```

---

## 🔍 Testing Checklist

Use this checklist when testing:

### ✅ Installation & Setup
- [ ] Python and Node.js installed
- [ ] Bootstrap script runs without errors
- [ ] Both servers start successfully
- [ ] Dashboard opens at http://localhost:3000

### ✅ User Interface
- [ ] Page loads correctly (no blank screen)
- [ ] Sidebar shows client list
- [ ] All 4 tabs are clickable
- [ ] Navigation works smoothly
- [ ] No console errors (press F12 to check)

### ✅ Dashboard Tab
- [ ] Summary cards show data
- [ ] Transaction table populates
- [ ] Filters work (client, report type, market type)
- [ ] Charts render correctly
- [ ] Data updates when filters change

### ✅ Energy Schedule Tab
- [ ] Hourly view works
- [ ] Daily view works
- [ ] Weekly view works
- [ ] Monthly view works
- [ ] Charts update when switching views
- [ ] Data tables show correct values

### ✅ Analytics Tab
- [ ] All 6 charts render
- [ ] Data filters by selected client
- [ ] Client name chip appears when filtered
- [ ] Charts are interactive (hover tooltips)

### ✅ Reports Tab
- [ ] Daily Trading PDF downloads
- [ ] Daily Trading Excel downloads
- [ ] Energy Schedule PDF downloads
- [ ] Downloaded files open correctly
- [ ] Data in reports is accurate

### ✅ Data Accuracy
- [ ] Numbers make sense (no NaN or undefined)
- [ ] Dates are formatted correctly
- [ ] Calculations appear accurate
- [ ] Charts match table data

---

## 💬 Providing Feedback

When testing, please note:

**What Works Well:**
- Features you like
- UI elements that are clear/intuitive
- Calculations that look accurate

**What Needs Improvement:**
- Confusing UI elements
- Missing features
- Incorrect calculations
- Performance issues
- Bugs or errors

**Domain-Specific Feedback:**
- Are IEX trading concepts represented correctly?
- Do calculations match industry standards?
- Is terminology accurate?
- What features are missing for real-world use?

---

## 🚀 Next Steps After Testing

If the application works well:

1. **Upload Real Data**
   - Place IEX Excel reports in a folder
   - Use upload feature to parse them
   - Verify data appears correctly

2. **Customize for Your Needs**
   - Modify calculations if needed
   - Add new report types
   - Adjust UI/branding

3. **Deploy to Production**
   - See `DEPLOYMENT_GUIDE.md` for hosting options
   - Free options available (Vercel, Render, Railway)

---

## 📞 Support

If you encounter issues:

1. **Check Logs:**
   - `backend.log` - Backend server logs
   - `frontend.log` - Frontend server logs

2. **View in Browser Console:**
   - Press `F12` in browser
   - Check Console tab for errors
   - Check Network tab for failed requests

3. **Common Solutions:**
   - Restart: Run bootstrap again
   - Clean install: Delete `node_modules`, `power_trading.db`, run bootstrap
   - Update: `pip install --upgrade pip` and `npm install -g npm`

---

## ⏱️ Expected Performance

- **First load**: 2-5 seconds
- **Dashboard rendering**: < 1 second
- **Chart updates**: Instant
- **Report generation**: 2-3 seconds
- **File upload/parse**: 5-10 seconds per file

If it's slower, check:
- System resources (RAM, CPU)
- Browser (try Chrome/Firefox)
- Antivirus (may slow file operations)

---

## 🎉 Summary

**To run this application:**

1. Install Python + Node.js
2. Run `bootstrap.sh` (macOS/Linux) or `bootstrap.bat` (Windows)
3. Open http://localhost:3000
4. Test all features
5. Provide feedback!

**No cloud costs, no hosting fees, no accounts needed.**  
Everything runs locally on your machine.

Enjoy testing! 🚀
